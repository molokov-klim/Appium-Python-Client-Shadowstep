# shadowstep/logging/shadowstep_logcat.py

import threading
import time
import logging
from typing import Callable, Optional
from websocket import create_connection, WebSocketConnectionClosedException, WebSocket
from selenium.common import WebDriverException

logger = logging.getLogger(__name__)


class ShadowstepLogcat:
    """
    Фоновый приёмник Android logcat через Appium 'mobile: startLogsBroadcast'.
    Работает в своём потоке, не блокирует основной код.
    """

    def __init__(
        self,
        driver_getter: Callable[[], 'WebDriver'],  # функция, возвращающая актуальный driver
        poll_interval: float = 1.0
    ):
        self._driver_getter = driver_getter
        self._poll_interval = poll_interval

        self._thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        self._filename: Optional[str] = None
        self._ws: Optional[WebSocket] = None  # <-- храним текущее соединение

    def __del__(self):
        self.stop()

    def start(self, filename: str) -> None:
        """
        Запуск фонового приёма logcat в файл (append).
        Немедленно возвращает управление — поток откроет файл и начнёт писать.
        """
        if self._thread and self._thread.is_alive():
            logger.info("Logcat already running")
            return

        self._stop_evt.clear()
        self._filename = filename
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="ShadowstepLogcat"
        )
        self._thread.start()
        logger.info(f"Started logcat to '{filename}'")

    def stop(self) -> None:
        """
        Остановка приёма и отсылка команды Appium для остановки broadcast.
        Пытаемся сразу закрыть WS, чтобы _run ушёл из recv().
        """
        if not self._thread:
            return

        self._stop_evt.set()

        # 1) закрыть WebSocket, если он открыт, чтобы прервать recv()
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass

        # 2) отослать команду stopLogsBroadcast
        try:
            driver = self._driver_getter()
            driver.execute_script("mobile: stopLogsBroadcast")
        except WebDriverException as e:
            logger.warning(f"Failed to stop broadcast: {e!r}")

        logger.info("Logcat stop requested (thread will shut down shortly)")

    def _run(self):
        """
        Главный цикл:
         - открываем файл
         - в цикле (пока не stop_evt):
             1) запускаем broadcast
             2) пробуем подключиться к двум WS-эндпоинтам
             3) читаем ws.recv() и пишем в файл
             4) при закрытии WS — переподключаемся через poll_interval
         - по выходу из внешнего цикла закрываем файл
        """
        if not self._filename:
            logger.error("No filename specified for logcat")
            return

        try:
            f = open(self._filename, "a", buffering=1, encoding="utf-8")
        except Exception as e:
            logger.error(f"Cannot open logcat file '{self._filename}': {e!r}")
            return

        try:
            while not self._stop_evt.is_set():
                try:
                    # 1) Запускаем broadcast
                    driver = self._driver_getter()
                    driver.execute_script("mobile: startLogsBroadcast")

                    # 2) Формируем базовый ws:// URL
                    session_id = driver.session_id
                    http_url = driver.command_executor._url
                    scheme, rest = http_url.split("://", 1)
                    ws_scheme = "ws" if scheme == "http" else "wss"
                    base_ws = f"{ws_scheme}://{rest}".rstrip("/wd/hub")

                    # 3) Пробуем оба эндпоинта
                    endpoints = [
                        f"{base_ws}/ws/session/{session_id}/appium/logcat",
                        f"{base_ws}/ws/session/{session_id}/appium/device/logcat",
                    ]
                    ws = None
                    for url in endpoints:
                        try:
                            ws = create_connection(url, timeout=5)
                            logger.info(f"Logcat WebSocket connected: {url}")
                            break
                        except Exception as ex:
                            logger.debug(f"Cannot connect to {url}: {ex!r}")
                    if not ws:
                        raise RuntimeError("Cannot connect to any logcat WS endpoint")

                    # сохраним ws, чтобы stop() мог его закрыть
                    self._ws = ws

                    # 4) Читаем до stop_evt
                    while not self._stop_evt.is_set():
                        try:
                            line = ws.recv()
                            f.write(line + "\n")
                        except WebSocketConnectionClosedException:
                            break  # переподключимся
                        except Exception as ex:
                            logger.debug(f"Ignoring recv error: {ex!r}")
                            continue

                    # очистить ссылку и закрыть сокет
                    try:
                        ws.close()
                    except Exception:
                        pass
                    finally:
                        self._ws = None

                    # пауза перед переподключением
                    time.sleep(self._poll_interval)

                except Exception as inner:
                    logger.error(f"Logcat stream error, retry in {self._poll_interval}s: {inner!r}", exc_info=True)
                    time.sleep(self._poll_interval)

        finally:
            try:
                f.close()
            except Exception:
                pass
            logger.info("Logcat thread terminated, file closed")
