import json
import logging
import requests
from icecream import ic
from lxml import etree

from shadowstep.element.element import Element
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.translator import YandexTranslate
from tests.conftest import APPIUM_IP, APPIUM_COMMAND_EXECUTOR, CAPABILITIES, APPIUM_PORT

def walk(el, level=0):
    ic(f"{type(el)} {el.attrib}")
    for child in el:
        walk(child, level + 1)



app = Shadowstep()
app.connect(server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            command_executor=APPIUM_COMMAND_EXECUTOR,
            capabilities=CAPABILITIES)

page_source = app.driver.page_source
parser = etree.XMLParser(recover=True)
root = etree.fromstring(page_source.encode("utf-8"), parser=parser)

walk(root)



"""
Каждый элемент (Element) имеет:
tag — имя узла (android.widget.LinearLayout)
attrib — словарь атрибутов ({"index": "0", "resource-id": "...", "text": "..."})
.text — текстовое содержимое (обычно пустое в Android page_source)
.getchildren() или просто итерация по element — доступ к вложенным узлам.
"""

"""

получение атрибутов элемента по локаторам шадоустеп

"""
