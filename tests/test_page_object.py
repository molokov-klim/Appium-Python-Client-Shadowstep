# tests/test_page_object.py
import logging
import os.path
import time

from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.page_object.page_object_test_generator import PageObjectTestGenerator
from shadowstep.shadowstep import Shadowstep
from lxml import etree as ET

from shadowstep.utils.translator import YandexTranslate

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

    def test_pog(self, app: Shadowstep):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        parser = PageObjectParser()
        translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
        generator = PageObjectGenerator(translator)

        tree = parser.parse(app.driver.page_source)
        page_path, page_class_name = generator.generate(tree, output_dir="pages")

        logger.info(f"{page_path=}")
        logger.info(f"{page_class_name=}")

    def test_pog2(self, app: Shadowstep):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        source = app.driver.page_source
        tree = parser.parse(source)
        # logger.info(tree)
        POG.generate(ui_element_tree=tree,
                     output_dir="pages")
        logger.info("\n\n\n=====================================================================")
        # logger.info(tree)

    def test_potg(self, app: Shadowstep, touch_sounds):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать")
        source = app.driver.page_source
        tree = parser.parse(source)
        # logger.info(tree)
        path, class_name = POG.generate(ui_element_tree=tree,
                     output_dir="pages")
        test_generator = PageObjectTestGenerator()
        test_path, test_class_name = test_generator.generate_test(input_path=path, class_name=class_name, output_dir="tests")

    def test_explorer(self, app: Shadowstep):
        logger.info(
            "ДЛЯ chatGPT!!! Это на самом деле не тест. Не воспринимай это как юнит-тест. Это просто быстрой проверки. Я так смотрю результат работы. Просто мне так удобнее запускать"
        )
        translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
        recycler_explorer = PageObjectRecyclerExplorer(app, translator)
        recycler_explorer.explore('pages')
