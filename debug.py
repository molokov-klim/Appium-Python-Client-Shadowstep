# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# debug.py
# type: ignore
# noqa
import logging

from shadowstep.enums import GestureStrategy
from shadowstep.shadowstep import Shadowstep
from tests.test_integro.conftest import (
    APPIUM_COMMAND_EXECUTOR,
    APPIUM_IP,
    APPIUM_PORT,
    CAPABILITIES,
)

logger = logging.getLogger(__name__)

app = Shadowstep()
app.connect(
    server_ip=APPIUM_IP,
    server_port=APPIUM_PORT,
    command_executor=APPIUM_COMMAND_EXECUTOR,
    capabilities=CAPABILITIES,
)

logger.info(app.driver.page_source)

LOCATOR_CONNECTED_DEVICES = {"text": "Connected devices"}
LOCATOR_SCROLL_VIEW = {"resource-id": "com.android.settings:id/main_content_scrollable_container"}
element = app.get_element(locator=LOCATOR_SCROLL_VIEW)

element.scroll_to_bottom(strategy=GestureStrategy.W3C_ACTIONS)
element.scroll_to_top(strategy=GestureStrategy.W3C_ACTIONS)
element.scroll_to_element(locator={"text": "System"}, strategy=GestureStrategy.W3C_ACTIONS)
assert element.is_displayed(), "JOPA BLYA"
