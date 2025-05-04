# shadowstep/terminal/terminal.py

import logging
import os
import re
import subprocess
import sys
import time
import traceback
import inspect
import base64
from typing import Any, Union, Tuple

from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchDriverException, InvalidSessionIdException

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NotProvideCredentials(Exception):
    def __init__(self, message='Not provided credentials for ssh connection '
                               'in connect() method (ssh_username, ssh_password)'):
        super().__init__(message)
        self.message = message


class Terminal:
    """
    Allows you to perform adb actions using the appium server. Useful for remote connections
    Required ssh
    """
    base: "Shadowstep" = None
    transport: "Transport" = None
    driver: WebDriver = None

    def __init__(self, base: "Shadowstep"):
        self.base: "Shadowstep" = base
        self.transport: "Transport" = base.transport
        self.driver: WebDriver = base.driver

    def __del__(self):
        if self.transport is not None:
            self.transport.ssh.close()

    def adb_shell(self, command: str, args: str = "", tries: int = 3) -> Any:
        """
        Method for executing commands via ADB on a mobile device.

        :param command: The command to execute.
        :param args: Additional arguments for the command (optional).
        :param tries: Number of attempts to execute the command in case of failure (default is 3).
        :return: The result of executing the command.
        """
        for _ in range(tries):
            try:
                return self.driver.execute_script("mobile: shell", {'command': command, 'args': [args]})
            except NoSuchDriverException:
                self.base.reconnect()
            except InvalidSessionIdException:
                self.base.reconnect()
            except KeyError as e:
                logger.error(e)
                traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
                logger.error(traceback_info)

    def push(self, source_path: str, remote_server_path: str, filename: str, destination: str, udid: str) -> bool:
        """
        Method for pushing files from a local source to a remote destination on a mobile device via ADB.

        :param source_path: The local path of the file to push.
        :param remote_server_path: The remote path on the server where the file will be pushed.
        :param filename: The name of the file to push.
        :param destination: The destination path on the mobile device.
        :param udid: The unique device identifier of the mobile device.
        :return: True if the file was successfully pushed, False otherwise.
        """
        if self.transport is None:
            raise NotProvideCredentials
        try:
            source_file_path = os.path.join(source_path, filename)
            remote_file_path = os.path.join(remote_server_path, filename)
            destination_file_path = f"{destination}/{filename}"
            self.transport.scp.put(files=source_file_path, remote_path=remote_file_path)
            stdin, stdout, stderr = self.transport.ssh.exec_command(
                f'adb -s {udid} push {remote_file_path} {destination_file_path}')
            stdout_exit_status = stdout.channel.recv_exit_status()
            lines = stdout.readlines()
            output = ''.join(lines)
            if stdout_exit_status != 0:
                logger.error(f"{inspect.currentframe().f_code.co_name} {output=}")
                return False
            logger.debug(f"{inspect.currentframe().f_code.co_name} {output=}")
            return True
        except NoSuchDriverException:
            self.base.reconnect()
        except InvalidSessionIdException:
            self.base.reconnect()
        except IOError as e:
            logger.error("push()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def pull(self, source: str, destination: str) -> bool:
        """
        Method for pulling a file from a mobile device to a local destination.

        :param source: The path of the file on the mobile device to pull.
        :param destination: The local path where the pulled file will be saved.
        :return: True if the file was successfully pulled, False otherwise.
        :raises NoSuchDriverException: If the WebDriver session does not exist.
        :raises InvalidSessionIdException: If the session ID is not valid.
        :raises IOError: If an I/O error occurs during file handling.
        """
        try:
            file_contents_base64 = self.driver.assert_extension_exists('mobile: pullFile'). \
                execute_script('mobile: pullFile', {'remotePath': source})
            if not file_contents_base64:
                return False
            decoded_contents = base64.b64decode(file_contents_base64)
            with open(destination, 'wb') as file:
                file.write(decoded_contents)
            return True
        except NoSuchDriverException:
            self.base.reconnect()
        except InvalidSessionIdException:
            self.base.reconnect()
        except IOError as e:
            logger.error("appium_extended_terminal.pull")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def start_activity(self, package: str, activity: str) -> bool:
        """
        Starts activity on the device.

        :param package: The package name of the application.
        :param activity: The activity to start.
        :return: True if the activity was started successfully, False otherwise.
        :raises KeyError: If the command fails due to missing keys in the response.
        """
        try:
            self.adb_shell(command="am", args=f"start -n {package}/{activity}")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.start_activity()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def get_current_app_package(self) -> Union[str, None]:
        """
        Retrieves the package name of the currently focused application on the device.

        :return: The package name of the currently focused application, or None if it cannot be determined.
        """
        try:
            result = self.adb_shell(command="dumpsys", args="window windows")
            lines = result.split('\n')
            for line in lines:
                if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                    matches = re.search(r'(([A-Za-z]{1}[A-Za-z\d_]*\.)+([A-Za-z][A-Za-z\d_]*)/)', line)
                    if matches:
                        return matches.group(1)[:-1]  # removing trailing slash
            return None
        except KeyError as e:
            logger.error("appium_extended_terminal.get_current_app_package()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return None

    def close_app(self, package: str) -> bool:
        """
        Closes the specified application on the device.

        :param package: The package name of the application to close.
        :return: True if the application was closed successfully, False otherwise.
        :raises KeyError: If the command fails due to missing keys in the response.
        """
        try:
            self.adb_shell(command="am", args=f"force-stop {package}")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.close_app()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def reboot_app(self, package: str, activity: str) -> bool:
        """
        Restarts the specified application on the device by closing it and then starting it again.

        :param package: The package name of the application to reboot.
        :param activity: The activity to start after rebooting the application.
        :return: True if the application was successfully rebooted, False otherwise.
        """
        if not self.close_app(package=package):
            return False
        if not self.start_activity(package=package, activity=activity):
            return False
        return True

    def install_app(self, source: str, remote_server_path: str, filename: str, udid: str) -> bool:
        """
        Installs an application on the specified mobile device.

        :param source: The local path of the application file to install.
        :param remote_server_path: The remote path on the server where the application file will be stored temporarily.
        :param filename: The name of the application file.
        :param udid: The unique device identifier (UDID) of the target mobile device.
        :return: True if the application was successfully installed, False otherwise.
        :raises NotProvideCredentials: If the transport credentials are not provided.
        """
        if self.transport is None:
            raise NotProvideCredentials
        try:
            source_filepath = os.path.join(source, filename)
            destination_filepath = os.path.join(remote_server_path, filename)
            self.transport.scp.put(files=source_filepath, remote_path=destination_filepath)
            stdin, stdout, stderr = self.transport.ssh.exec_command(
                f'adb -s {udid} install -r {destination_filepath}')
            stdout_exit_status = stdout.channel.recv_exit_status()
            lines = stdout.readlines()
            output = ''.join(lines)
            if stdout_exit_status != 0:
                logger.error(f"{inspect.currentframe().f_code.co_name} {output=}")
                return False
            logger.debug(f"{inspect.currentframe().f_code.co_name} {output=}")
            return True
        except IOError as e:
            logger.error("appium_extended_terminal.push()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def is_app_installed(self, package) -> bool:
        """
        Checks if the specified application package is installed on the device.

        :param package: The package name of the application to check.
        :return: True if the application is installed, False otherwise.
        """
        logger.debug(f"is_app_installed() < {package=}")

        try:
            result = self.adb_shell(command="pm", args="list packages")
            if any([line.strip().endswith(package) for line in result.splitlines()]):
                logger.debug("is_app_installed() > True")
                return True
            logger.debug("is_app_installed() > False")
            return False
        except KeyError as e:
            logger.error("appium_extended_terminal.is_app_installed() > False")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def uninstall_app(self, package: str) -> bool:
        """
        Uninstalls the specified application from the device.

        :param package: The package name of the application to uninstall.
        :return: True if the application was successfully uninstalled, False otherwise.
        """
        try:
            self.driver.remove_app(app_id=package)
            return True
        except NoSuchDriverException:
            self.base.reconnect()
        except InvalidSessionIdException:
            self.base.reconnect()
        except KeyError as e:
            logger.error("appium_extended_terminal.uninstall_app()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def press_home(self) -> bool:
        """
        Simulates pressing the home button on the device.

        :return: True if the home button press was successfully simulated, False otherwise.
        """
        try:
            self.input_keycode(keycode="KEYCODE_HOME")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.press_home()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def press_back(self) -> bool:
        """
        Simulates pressing the back button on the device.

        :return: True if the back button press was successfully simulated, False otherwise.
        """

        try:
            self.input_keycode(keycode="KEYCODE_BACK")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.press_back()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def press_menu(self) -> bool:
        """
        Simulates pressing the menu button on the device.

        :return: True if the menu button press was successfully simulated, False otherwise.
        """

        try:
            self.input_keycode(keycode="KEYCODE_MENU")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.press_menu()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def input_keycode_num_(self, num: int) -> bool:
        """
        Sends a numeric key event to the device using ADB.
        0-9, ADD, COMMA, DIVIDE, DOT, ENTER, EQUALS (read https://developer.android.com/reference/android/view/KeyEvent)

        :param num: The numeric value of the key to press.
        :return: True if the command was executed successfully, False otherwise.
        """
        try:
            self.adb_shell(command="input", args=f"keyevent KEYCODE_NUMPAD_{num}")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.input_keycode_num_()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def input_keycode(self, keycode: str) -> bool:
        """
        Sends a key event to the device using ADB.

        :param keycode: The keycode to send to the device.
        :return: True if the command was executed successfully, False otherwise.
        """
        try:
            self.adb_shell(command="input", args=f"keyevent {keycode}")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.input_keycode()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def input_text(self, text: str) -> bool:
        """
        Inputs text on the device.

        :param text: The text to input.
        :return: True if the text was successfully inputted, False otherwise.
        """
        try:
            self.adb_shell(command="input", args=f"text {text}")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.input_text()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def tap(self, x: int, y: int) -> bool:
        """
        Simulates tapping at the specified coordinates on the device's screen.

        :param x: The x-coordinate of the tap.
        :param y: The y-coordinate of the tap.
        :return: True if the tap was successful, False otherwise.
        """
        try:
            self.adb_shell(command="input", args=f"tap {str(x)} {str(y)}")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.tap()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def swipe(self, start_x: Union[str, int], start_y: Union[str, int],
              end_x: Union[str, int], end_y: Union[str, int], duration: int = 300) -> bool:
        """
        Simulates a swipe gesture from one point to another on the device's screen.

        :param start_x: The x-coordinate of the starting point of the swipe.
        :param start_y: The y-coordinate of the starting point of the swipe.
        :param end_x: The x-coordinate of the ending point of the swipe.
        :param end_y: The y-coordinate of the ending point of the swipe.
        :param duration: The duration of the swipe in milliseconds (default is 300).
        :return: True if the swipe was successful, False otherwise.
        """
        try:
            self.adb_shell(command="input",
                           args=f"swipe {str(start_x)} {str(start_y)} {str(end_x)} {str(end_y)} {str(duration)}")
            return True
        except KeyError as e:
            logger.error("appium_extended_terminal.swipe()")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def swipe_right_to_left(self, duration: int = 300) -> bool:
        """
        Simulates a swipe gesture from right to left on the device's screen.

        :param duration: The duration of the swipe in milliseconds (default is 300).
        :return: True if the swipe was successful, False otherwise.
        """
        window_size = self.get_screen_resolution()
        width = window_size[0]
        height = window_size[1]
        left = int(width * 0.1)
        right = int(width * 0.9)
        return self.swipe(start_x=right,
                          start_y=height // 2,
                          end_x=left,
                          end_y=height // 2,
                          duration=duration)

    def swipe_left_to_right(self, duration: int = 300) -> bool:
        """
        Simulates a swipe gesture from left to right on the device's screen.

        :param duration: The duration of the swipe in milliseconds (default is 300).
        :return: True if the swipe was successful, False otherwise.
        """
        window_size = self.get_screen_resolution()
        width = window_size[0]
        height = window_size[1]
        left = int(width * 0.1)
        right = int(width * 0.9)
        return self.swipe(start_x=left,
                          start_y=height // 2,
                          end_x=right,
                          end_y=height // 2,
                          duration=duration)

    def swipe_top_to_bottom(self, duration: int = 300) -> bool:
        """
        Simulates a swipe gesture from top to bottom on the device's screen.

        :param duration: The duration of the swipe in milliseconds (default is 300).
        :return: True if the swipe was successful, False otherwise.
        """
        window_size = self.get_screen_resolution()
        height = window_size[1]
        top = int(height * 0.1)
        bottom = int(height * 0.9)
        return self.swipe(start_x=top,
                          start_y=height // 2,
                          end_x=bottom,
                          end_y=height // 2,
                          duration=duration)

    def swipe_bottom_to_top(self, duration: int = 300) -> bool:
        """
        Simulates a swipe gesture from bottom to top on the device's screen.

        :param duration: The duration of the swipe in milliseconds (default is 300).
        :return: True if the swipe was successful, False otherwise.
        """
        window_size = self.get_screen_resolution()
        height = window_size[1]
        top = int(height * 0.1)
        bottom = int(height * 0.9)
        return self.swipe(start_x=bottom,
                          start_y=height // 2,
                          end_x=top,
                          end_y=height // 2,
                          duration=duration)

    def check_vpn(self, ip_address: str = '') -> bool:
        """
        Checks if a VPN connection is established on the device.

        :param ip_address: Optional IP address to check for VPN connection (default is '').
        :return: True if a VPN connection is established, False otherwise.
        """
        try:
            output = self.adb_shell(command="netstat", args="")
            lines = output.split('\n')
            for line in lines:
                if ip_address in line and "ESTABLISHED" in line:
                    logger.debug("check_VPN() True")
                    return True
            logger.debug("check_VPN() False")
            return False
        except KeyError as e:
            logger.error("appium_extended_terminal.check_VPN")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def stop_logcat(self) -> bool:
        """
        Stops the logcat process running on the device.

        :return: True if the logcat process was successfully stopped, False otherwise.
        """
        try:
            process_list = self.adb_shell(command="ps", args="")
        except KeyError as e:
            logger.error("appium_extended_terminal.stop_logcat")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False
        for process in process_list.splitlines():
            if "logcat" in process:
                pid = process.split()[1]
                try:
                    self.adb_shell(command="kill", args=f"-SIGINT {str(pid)}")
                except KeyError as e:
                    logger.error("appium_extended_terminal.stop_logcat")
                    logger.error(e)
                    traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
                    logger.error(traceback_info)
                    return False
        return True

    def know_pid(self, name: str) -> Union[int, None]:
        """
        Retrieves the process ID (PID) of the specified process name.

        :param name: The name of the process.
        :return: The PID of the process if found, None otherwise.
        """
        processes = self.adb_shell(command="ps")
        if name not in processes:
            logger.error("know_pid() [Процесс не обнаружен]")
            return None
        lines = processes.strip().split('\n')
        for line in lines[1:]:
            columns = line.split()
            if len(columns) >= 9:
                pid, process_name = columns[1], columns[8]
                if name == process_name:
                    logger.debug(f"know_pid() > {str(pid)}")
                    return int(pid)
        logger.error("know_pid() [Процесс не обнаружен]")
        return None

    def is_process_exist(self, name: str) -> bool:
        """
        Checks if a process with the specified name exists.

        :param name: The name of the process.
        :return: True if the process exists, False otherwise.
        """
        processes = self.adb_shell(command="ps")
        if name not in processes:
            logger.debug("is_process_exist() > False")
            return False
        lines = processes.strip().split('\n')
        for line in lines[1:]:
            columns = line.split()
            if len(columns) >= 9:
                _, process_name = columns[1], columns[8]
                if name == process_name:
                    logger.debug("is_process_exist() > True")
                    return True
        logger.debug("is_process_exist() > False")
        return False

    def run_background_process(self, command: str, args: str = "", process: str = "") -> bool:
        """
        Runs a background process on the device using the specified command.

        :param command: The command to run.
        :param args: Additional arguments for the command (default is "").
        :param process: The name of the process to check for existence (default is "").
        :return: True if the background process was successfully started, False otherwise.
        """
        logger.debug(f"run_background_process() < {command=}")

        try:
            self.adb_shell(command=command, args=args + " nohup > /dev/null 2>&1 &")
            if process != "":
                time.sleep(1)
                if not self.is_process_exist(name=process):
                    return False
            return True
        except KeyError as e:
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False

    def kill_by_pid(self, pid: int) -> bool:
        """
        Kills the process with the specified PID.

        :param pid: The process ID (PID) of the process to kill.
        :return: True if the process was successfully killed, False otherwise.
        """
        try:
            self.adb_shell(command="kill", args=f"-s SIGINT {str(pid)}")
        except KeyError as e:
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False
        return True

    def kill_by_name(self, name: str) -> bool:
        """
        Kills the process with the specified name.

        :param name: The name of the process to kill.
        :return: True if the process was successfully killed, False otherwise.
        """
        logger.debug(f"kill_by_name() < {name=}")
        try:
            self.adb_shell(command="pkill", args=f"-l SIGINT {str(name)}")
        except KeyError as e:
            logger.error("kill_by_name() > False")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False
        logger.debug("kill_by_name() > True")
        return True

    def kill_all(self, name: str) -> bool:
        """
        Kills all processes with the specified name.

        :param name: The name of the processes to kill.
        :return: True if the processes were successfully killed, False otherwise.
        """
        try:
            self.adb_shell(command="pkill", args=f"-f {str(name)}")
        except KeyError as e:
            logger.error("appium_extended_terminal.kill_all")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False
        return True

    def delete_files_from_internal_storage(self, path) -> bool:
        """
        Deletes files from the internal storage of the device.

        :param path: The path of the files to delete.
        :return: True if the files were successfully deleted, False otherwise.
        """
        try:
            self.adb_shell(command="rm", args=f"-rf {path}*")
        except KeyError as e:
            logger.error("appium_extended_terminal.delete_files_from_internal_storage")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False
        return True

    def delete_file_from_internal_storage(self, path: str, filename: str) -> bool:
        """
        Deletes a file from the internal storage of the device.

        :param path: The path of the file's directory.
        :param filename: The name of the file to delete.
        :return: True if the file was successfully deleted, False otherwise.
        """
        try:
            if path.endswith('/'):
                path = path[:-1]
            self.adb_shell(command="rm", args=f"-rf {path}/{filename}")
        except KeyError as e:
            logger.error("appium_extended_terminal.delete_file_from_internal_storage")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False
        return True

    def record_video(self, **options: Any) -> bool:
        """
        Records a video of the device screen (3 MIN MAX).

        :param options: Additional options for video recording.
        :return: True if the video recording started successfully, False otherwise.
        """
        try:
            self.driver.start_recording_screen(**options)
        except NoSuchDriverException:
            self.base.reconnect()
        except InvalidSessionIdException:
            self.base.reconnect()
        except KeyError as e:
            logger.error("appium_extended_terminal.record_video")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return False
        return True

    def stop_video(self, **options: Any) -> Union[bytes, None]:
        """
        Stops the video recording of the device screen and returns the recorded video data (Base64 bytes).

        :param options: Additional options for stopping the video recording.
        :return: The recorded video data as bytes if the recording stopped successfully, None otherwise.
        """
        try:
            str_based64_video = self.driver.stop_recording_screen(**options)
            return base64.b64decode(str_based64_video)
        except NoSuchDriverException:
            self.base.reconnect()
        except InvalidSessionIdException:
            self.base.reconnect()
        except KeyError as e:
            logger.error("appium_extended_terminal.stop_video")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)
            return None

    def reboot(self) -> bool:
        """
        Reboots the device safely. If adb connection drops, ignores the error.
        """
        try:
            self.adb_shell(command='reboot')
            return True
        except Exception as e:
            logger.warning(f"Reboot likely initiated. Caught exception: {e}")
            return True

    def get_screen_resolution(self) -> Union[Tuple[int, int], None]:
        """
        Retrieves the screen resolution of the device.

        :return: A tuple containing the width and height of the screen in pixels if successful,
                 or None if the resolution couldn't be retrieved.
        """
        try:
            output = self.adb_shell(command='wm', args='size')
            if "Physical size" in output:
                resolution_str = output.split(":")[1].strip()
                width, height = resolution_str.split("x")
                return int(width), int(height)
        except KeyError as e:
            logger.error("appium_extended_terminal.get_screen_resolution")
            logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            logger.error(traceback_info)

    def past_text(self, text: str, tries: int = 3) -> None:
        """
        Помещает в буфер обмена заданный текст, затем вставляет его
        """
        for _ in range(tries):
            try:
                self.driver.set_clipboard_text(text=text)
                self.input_keycode('279')
                return
            except NoSuchDriverException:
                self.base.reconnect()
            except InvalidSessionIdException:
                self.base.reconnect()

    def get_prop(self) -> dict:
        """
        Retrieves system properties from the device.

        :return: A dictionary containing the system properties as key-value pairs.
        """
        raw_properties = self.adb_shell(command="getprop")
        lines = raw_properties.replace("\r", "").strip().split("\n")
        result_dict = {}
        for line in lines:
            try:
                key, value = line.strip().split(":", 1)
                key = key.strip()[1:-1]
                value = value.strip()[1:-1]
                result_dict[key] = value
            except ValueError:
                continue

        return result_dict

    def get_prop_hardware(self) -> str:
        """
        Retrieves the hardware information from the system properties of the device.

        :return: A string representing the hardware information.
        """
        return self.get_prop()['ro.boot.hardware']

    def get_prop_model(self) -> str:
        """
        Retrieves the model name of the device from the system properties.

        :return: A string representing the model name of the device.
        """
        return self.get_prop()['ro.product.model']

    def get_prop_serial(self) -> str:
        """
        Retrieves the serial number of the device from the system properties.

        :return: A string representing the serial number of the device.
        """
        return self.get_prop()['ro.serialno']

    def get_prop_build(self) -> str:
        """
        Retrieves the build description from the system properties.

        :return: A string representing the build description of the device.
        """
        return self.get_prop()['ro.build.description']

    def get_prop_device(self) -> str:
        """
        Retrieves the device name from the system properties.

        :return: A string representing the device name.
        """
        return self.get_prop()['ro.product.device']

    def get_prop_uin(self) -> str:
        """
        Retrieves the unique identification number (UIN) from the system properties.

        :return: A string representing the unique identification number.
        """
        return self.get_prop()['sys.atol.uin']

    def get_packages(self) -> list:
        """
        Retrieves the list of installed packages on the device.

        :return: A list of package names.
        """
        output = self.adb_shell(command='pm', args='list packages')
        lines = output.strip().split('\n')
        packages = [line.split(':')[-1].replace('\r', '') for line in lines]
        return packages

    def get_package_path(self, package: str) -> str:
        """
        Retrieves the path to the APK file associated with the given package.

        :param package: The name of the package.
        :return: The path to the APK file.
        """
        return self.adb_shell(command='pm', args=f'path {package}'). \
            replace('package:', ''). \
            replace('\r', ''). \
            replace('\n', '')

    def pull_package(self, package: str, path: str = '', filename: str = 'temp.apk'):
        """
        Pulls the APK file of the specified package from the device to the local machine.

        :param package: The package name of the app.
        :param path: The local path where the APK file will be saved. Default is current directory.
        :param filename: The name of the APK file. If not provided, a default name 'temp.apk' will be used.
        """
        package_path = self.get_package_path(package=package)
        if not filename.endswith('.apk'):
            filename = f"{filename}.apk"
        self.pull(source=package_path, destination=os.path.join(path, filename))

    def get_package_manifest(self, package: str) -> dict:
        """
        Retrieves the manifest of the specified package from the device.

        :param package: The package name of the app.
        :return: A dictionary representing the package manifest.
        """
        if not os.path.exists("test"):
            os.makedirs(name='test')

        self.pull_package(package=package, path="test",
                          filename="temp.apk")

        command = ["aapt", "dump", "badging", os.path.join("test", "temp.apk")]
        try:
            output: str = str(subprocess.check_output(command)).strip()
        except subprocess.CalledProcessError as error:
            return {}
        output = output.replace('\\r\\n', ' ').replace('b"', '').replace('"', '').replace(":'", ": '")
        list_of_elements = output.split()
        result = {}
        current_key = None

        for element in list_of_elements:
            if element.endswith(':'):
                result[element] = []
                current_key = element
                continue
            result[current_key].append(element.replace("'", ""))

        os.remove(os.path.join('test', 'temp.apk'))

        return result
