# tests/test_page_object_extractor.py
import logging
import time

from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.page_object.page_object_extractor import PageObjectExtractor
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.shadowstep import Shadowstep
from lxml import etree as ET

POE = PageObjectExtractor()
logger = logging.getLogger(__name__)

class TestPageObjectextractor:

    def test_poe(self, app: Shadowstep, android_settings):
        logger.info("ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        source = app.driver.page_source
        logger.info("\n\n\n=============================== RAW ======================================")
        POE.parse(source)
        logger.info("\n\n\n=====================================================================")
        logger.info(source)

    def test_pog(self, app: Shadowstep, android_settings):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        app.find_and_get_element({'text': 'Sound & vibration'}).tap()
        time.sleep(5)
        app.find_and_get_element({'text': 'Touch sounds'})
        time.sleep(5)
        generator = PageObjectGenerator(extractor=POE)
        source = app.driver.page_source
        generator.generate(source, output_dir="pages", attributes=['class',
                                                                   'text',
                                                                   'resource-id',
                                                                   'content-desc',
                                                                   'scrollable'])
        logger.info("\n\n\n=====================================================================")
        logger.info(source)

    def test_generated_page(self, app: Shadowstep, android_settings):
        from pages.page_sound_vibration import PageSoundVibration
        import time

        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать"
        )

        page = PageSoundVibration()
        app.find_and_get_element({'text': 'Sound & vibration'}).tap()
        time.sleep(5)

        logger.info("Проверяем: title")
        assert isinstance(page.title.get_attributes(), dict)

        logger.info("Проверяем: charging_sounds_and_vibration_textview")
        assert isinstance(page.charging_sounds_and_vibration_textview.get_attributes(), dict)

        logger.info("Проверяем: charging_sounds_and_vibration_switch")
        assert isinstance(page.charging_sounds_and_vibration_switch.get_attributes(), dict)

        logger.info("Проверяем: default_alarm_sound_textview")
        assert isinstance(page.default_alarm_sound_textview.get_attributes(), dict)

        logger.info("Проверяем: default_alarm_sound_summary_textview")
        assert isinstance(page.default_alarm_sound_summary_textview.get_attributes(), dict)

        logger.info("Проверяем: dial_pad_tones_textview")
        assert isinstance(page.dial_pad_tones_textview.get_attributes(), dict)

        logger.info("Проверяем: dial_pad_tones_switch")
        assert isinstance(page.dial_pad_tones_switch.get_attributes(), dict)

        logger.info("Проверяем: do_not_disturb_textview")
        assert isinstance(page.do_not_disturb_textview.get_attributes(), dict)

        logger.info("Проверяем: do_not_disturb_summary_textview")
        assert isinstance(page.do_not_disturb_summary_textview.get_attributes(), dict)

        logger.info("Проверяем: media_textview")
        assert isinstance(page.media_textview.get_attributes(), dict)

        logger.info("Проверяем: media_summary_textview")
        assert isinstance(page.media_summary_textview.get_attributes(), dict)

        logger.info("Проверяем: phone_ringtone_textview")
        assert isinstance(page.phone_ringtone_textview.get_attributes(), dict)

        logger.info("Проверяем: phone_ringtone_summary_textview")
        assert isinstance(page.phone_ringtone_summary_textview.get_attributes(), dict)

        logger.info("Проверяем: screen_locking_sound_textview")
        assert isinstance(page.screen_locking_sound_textview.get_attributes(), dict)

        logger.info("Проверяем: screen_locking_sound_switch")
        assert isinstance(page.screen_locking_sound_switch.get_attributes(), dict)

        logger.info("Проверяем: shortcut_to_prevent_ringing_textview")
        assert isinstance(page.shortcut_to_prevent_ringing_textview.get_attributes(), dict)

        logger.info("Проверяем: shortcut_to_prevent_ringing_summary_textview")
        assert isinstance(page.shortcut_to_prevent_ringing_summary_textview.get_attributes(), dict)

        logger.info("Проверяем: shortcut_to_prevent_ringing_switch")
        assert isinstance(page.shortcut_to_prevent_ringing_switch.get_attributes(), dict)

        logger.info("Проверяем: touch_sounds_textview")
        assert isinstance(page.touch_sounds_textview.get_attributes(), dict)

        logger.info("Проверяем: touch_sounds_switch")
        assert isinstance(page.touch_sounds_switch.get_attributes(), dict)





