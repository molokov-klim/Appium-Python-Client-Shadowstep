import logging

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
        POE.smart_filter = False
        POE.filter_by_class = False
        POE.filter_system = False
        raw_elements = POE.extract_simple_elements(source)
        for el in raw_elements:
            logger.info(el)
        logger.info("\n\n\n=============================== FILTER ======================================")
        POE.package = 'com.android.settings'
        raw_elements = POE.extract_simple_elements(source)
        for el in raw_elements:
            logger.info(el)
        logger.info("\n\n\n=====================================================================")
        logger.info(source)

    def test_pog(self, app: Shadowstep, android_settings):
        generator = PageObjectGenerator(extractor=POE)
        source = app.driver.page_source
        generator.generate(source, output_dir="pages", attributes=['class',
                                                                   'text',
                                                                   'resource-id',
                                                                   'content-desc',
                                                                   'scrollable'])
        logger.info("\n\n\n=====================================================================")
        logger.info(source)
