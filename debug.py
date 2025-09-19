import json
import logging
import requests
from lxml import etree  # type: ignore

from shadowstep.element.element import Element
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.translator import YandexTranslate
from tests.conftest import APPIUM_IP, APPIUM_COMMAND_EXECUTOR, CAPABILITIES, APPIUM_PORT

app = Shadowstep()
app.connect(server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            command_executor=APPIUM_COMMAND_EXECUTOR,
            capabilities=CAPABILITIES)

page_source = app.driver.page_source
parser = etree.XMLParser(recover=True)
root = etree.fromstring(page_source.encode("utf-8"), parser=parser)
