# builder.py
import json  # type: ignore  # noqa: F401
import logging  # type: ignore  # noqa: F401

import requests  # type: ignore  # noqa: F401

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.translator import YandexTranslate
from tests.conftest import APPIUM_COMMAND_EXECUTOR, APPIUM_IP, APPIUM_PORT, CAPABILITIES

app = Shadowstep()
app.connect(server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            command_executor=APPIUM_COMMAND_EXECUTOR,
            capabilities=CAPABILITIES)

parser = PageObjectParser()
translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
generator = PageObjectGenerator(translator)
recycler_explorer = PageObjectRecyclerExplorer(app, translator)

# self.shadowstep.driver.update_settings(settings={'enableMultiWindows': True})
# time.sleep(10)

source = app.driver.page_source
print(source)
tree = parser.parse(source)
# generator.generate(ui_element_tree=tree, output_dir="pages")
recycler_explorer.explore("pages")

# self.shadowstep.driver.update_settings(settings={'enableMultiWindows': False})
