import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _translate(text: str) -> str:
    """
    Translate given text to English using LibreTranslate API (argosopentech mirror).

    Args:
        text (str): Input text to translate.

    Returns:
        str: Translated text in English.
    """
    logger.info(f"Translating: {text}")

    url = "https://translate.argosopentech.com/translate"  # <<<<<< ВОТ ЭТА ХУЙНЯ ЗАРАБОТАЕТ
    headers = {"Content-Type": "application/json"}
    payload = {
        "q": text,
        "source": "auto",
        "target": "en",
        "format": "text"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        translated = response.json().get("translatedText", "")
        logger.info(f"Translated: {translated}")
        return translated
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text


if __name__ == "__main__":
    logger.info("=== Manual Translation Test ===")
    print(_translate("Привет, мир"))           # → Hello, world
    print(_translate("こんにちは世界"))           # → Hello world
    print(_translate("Bonjour le monde"))      # → Hello the world
