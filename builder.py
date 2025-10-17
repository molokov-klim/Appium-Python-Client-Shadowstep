"""Builder module for Appium Python Client Shadowstep.

This module provides a builder script for testing and demonstrating
the Shadowstep framework functionality including page object generation,
parsing, and recycler exploration.
"""

# builder.py
import json  # type: ignore[import-untyped]  # noqa: F401
import logging  # type: ignore[import-untyped]  # noqa: F401

import requests  # type: ignore[import-untyped]  # noqa: F401

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from tests.test_integro.conftest import (
            APPIUM_COMMAND_EXECUTOR,
            APPIUM_IP,
            APPIUM_PORT,
            CAPABILITIES,
)

app = Shadowstep()
app.connect(server_ip=APPIUM_IP,
            server_port=APPIUM_PORT,
            command_executor=APPIUM_COMMAND_EXECUTOR,
            capabilities=CAPABILITIES)

parser = PageObjectParser()
#translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
generator = PageObjectGenerator()
recycler_explorer = PageObjectRecyclerExplorer(app, translator=None)

source = app.driver.page_source    # type: ignore[reportOptionalMemberAccess]
print(source)   # noqa: T201
tree = parser.parse(source)
recycler_explorer.explore("pages")
