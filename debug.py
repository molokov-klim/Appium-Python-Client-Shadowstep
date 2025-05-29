import json
import logging
import requests

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.utils.translator import YandexTranslate








logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = PageObjectParser()
translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
generator = PageObjectGenerator(translator)

tree = parser.parse(app.shadowstep.driver.page_source)
page_path, page_class_name = generator.generate(tree, output_dir="pages")

logger.info(f"{page_path=}")
logger.info(f"{page_class_name=}")












