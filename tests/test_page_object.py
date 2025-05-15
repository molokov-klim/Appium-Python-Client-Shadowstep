# tests/test_page_object.py
import logging
import os.path
import time

from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from lxml import etree as ET

parser = PageObjectParser()
POG = PageObjectGenerator()
logger = logging.getLogger(__name__)


class TestPageObjectextractor:

    def test_poe(self, app: Shadowstep, touch_sounds):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        source = app.driver.page_source
        logger.info("\n\n\n=============================== RAW ======================================\n\n\n")
        ui_element_tree = parser.parse(source)
        logger.info("\n\n\n=====================================================================\n\n\n")
        logger.info(f"{ui_element_tree=}")
        logger.info("\n\n\n=====================================================================\n\n\n")
        logger.info(f"{source=}")

    def test_pog(self, app: Shadowstep, touch_sounds):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        source = app.driver.page_source
        tree = parser.parse(source)
        # logger.info(tree)
        POG.generate(ui_element_tree=tree,
                     output_dir="pages")
        logger.info("\n\n\n=====================================================================")
        # logger.info(tree)

    # def test_pore(self, app: Shadowstep, touch_sounds):
    #     logger.info(
    #         "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать"
    #     )
    #     PORE = PageObjectRecyclerExplorer(app)
    #     source = app.driver.page_source
    #     path, class_name = POG.generate(source, output_dir="pages", attributes=['class',
    #                                                                             'text',
    #                                                                             'resource-id',
    #                                                                             'content-desc',
    #                                                                             'scrollable'])
    #     PORE.explore(path, class_name, path)
