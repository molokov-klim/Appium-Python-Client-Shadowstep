# tests/test_page_object_extractor.py
import logging
import os.path
import time

from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.page_object.page_object_extractor import PageObjectParser
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from lxml import etree as ET

POE = PageObjectParser()
POG = PageObjectGenerator(extractor=POE)
logger = logging.getLogger(__name__)


class TestPageObjectextractor:

    def test_poe(self, app: Shadowstep, android_settings):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        source = app.driver.page_source
        logger.info("\n\n\n=============================== RAW ======================================")
        POE.parse(source)
        logger.info("\n\n\n=====================================================================")
        logger.info(source)

    def test_pog(self, app: Shadowstep, android_settings):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        logger.info(f"tap to Sound & vibration")
        sound_and_vibration = app.find_and_get_element({'text': 'Sound & vibration'})
        logger.info(f"{sound_and_vibration.get_attributes()=}")
        sound_and_vibration.tap()


        time.sleep(5)
        logger.info(f"find_and_get_element Touch sounds")
        app.find_and_get_element({'text': 'Touch sounds'})
        time.sleep(5)
        source = app.driver.page_source
        POG.generate(source, output_dir="pages", attributes=['class',
                                                             'text',
                                                             'resource-id',
                                                             'content-desc',
                                                             'scrollable'])
        logger.info("\n\n\n=====================================================================")
        logger.info(source)

    def test_pore(self, app: Shadowstep, android_settings):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать"
        )
        app.find_and_get_element({'text': 'Sound & vibration'}).tap()
        time.sleep(5)
        app.find_and_get_element({'text': 'Touch sounds'})
        time.sleep(5)
        PORE = PageObjectRecyclerExplorer(app)
        source = app.driver.page_source
        path, class_name = POG.generate(source, output_dir="pages", attributes=['class',
                                                                                'text',
                                                                                'resource-id',
                                                                                'content-desc',
                                                                                'scrollable'])
        PORE.explore(path, class_name, path)
