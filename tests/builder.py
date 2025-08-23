from typing import Any

from conftest import APPIUM_IP, APPIUM_PORT, UDID

from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.translator import YandexTranslate

app = Shadowstep()

capabilities: dict[str, Any] = {
    "platformName": "android",
    "appium:automationName": "uiautomator2",
    "appium:UDID": UDID,
    "appium:noReset": True,
    "appium:autoGrantPermissions": True,
    "appium:newCommandTimeout": 900,
}

app.connect(capabilities=capabilities,
            server_ip=APPIUM_IP,
            server_port=APPIUM_PORT)

try:
    parser = PageObjectParser()
    translator = YandexTranslate(folder_id="b1ghf7n3imfg7foodstv")
    generator = PageObjectGenerator(translator)
    recycler_explorer = PageObjectRecyclerExplorer(app, translator)

    # self.shadowstep.driver.update_settings(settings={'enableMultiWindows': True})
    # time.sleep(10)

    source = app.driver.page_source
    print(source)
    tree = parser.parse(source)
    generator.generate(ui_element_tree=tree, output_dir="pages")
    # recycler_explorer.explore('pages')

    # self.shadowstep.driver.update_settings(settings={'enableMultiWindows': False})



except Exception as error:
    print("STOP STOP STOP STOP STOP STOP STOP STOP STOP STOP STOP STOP STOP ")
    print(error)
finally:
    try:
        app.disconnect()
    except Exception as e:
        if 'NoSuchSessionException' in str(e):
            print("Сессия уже завершена.")
        else:
            raise
