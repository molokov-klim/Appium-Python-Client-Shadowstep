import base64
import inspect
import logging
import traceback
import typing
from typing import Union, Tuple, Dict

import numpy as np
from PIL import Image
from appium.webdriver import WebElement
from selenium.common import WebDriverException
from selenium.types import WaitExcTypes

from shadowstep.base import ShadowstepBase
from shadowstep.element.element import Element

# Configure the root logger (basic configuration)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeneralShadowstepException(WebDriverException):
    """Raised when driver is not specified and cannot be located."""

    def __init__(
            self, msg: typing.Optional[str] = None, screen: typing.Optional[str] = None,
            stacktrace: typing.Optional[typing.Sequence[str]] = None
    ) -> None:
        super().__init__(msg, screen, stacktrace)


class Shadowstep(ShadowstepBase):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get_element(self,
                    locator: Union[Tuple[str, str], Dict[str, str]] = None,
                    timeout: int = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                    contains: bool = False) -> Element:
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        element = Element(locator=locator,
                          timeout=timeout,
                          poll_frequency=poll_frequency,
                          ignored_exceptions=ignored_exceptions,
                          contains=contains,
                          base=self)
        return element

    def get_elements(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_image(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_images(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_text(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError

    def scheduled_actions(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")
        # https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/scheduled-actions.md

    def find_and_get_element(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_image_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_inner_image_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_many_coordinates_of_image(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_text_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_text_on_screen(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_image_on_the_screen(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def to_ndarray(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_right_to_left(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_left_to_right(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_top_to_bottom(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def swipe_bottom_to_top(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def wait_for(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def wait_for_not(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_wait_for(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def is_wait_for_not(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def wait_return_true(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def draw_by_coordinates(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def save_screenshot(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def get_screenshot_as_base64_decoded(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        screenshot = self.driver.get_screenshot_as_base64().encode('utf-8')
        screenshot = base64.b64decode(screenshot)
        return screenshot

    def save_source(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def find_and_tap_in_drop_down_menu(self, *args, **kwargs):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        raise NotImplementedError(f"Method {inspect.currentframe().f_code.co_name} is not yet implemented.")

    def tap(
            self,
            locator: Union[Tuple[str, str], Dict[str, str], Element, WebElement] = None,
            x: int = None,
            y: int = None,
            image: Union[bytes, np.ndarray, Image.Image, str] = None,
            duration: typing.Optional[int] = None,
            timeout: float = 5.0,
            threshold: float = 0.9
    ) -> 'Shadowstep':
        """Perform tap action via locator, coordinates, image or element.

        Args:
            locator (Union[Tuple[str, str], Dict[str, str], Element, WebElement], optional): Element locator or object.
            x (int, optional): X coordinate to tap.
            y (int, optional): Y coordinate to tap.
            image (Union[bytes, np.ndarray, Image.Image, str], optional): Image to find and tap.
            duration (int, optional): Tap duration in milliseconds.
            timeout (float): Timeout for waiting elements or image match.
            threshold (float): Matching threshold for image recognition.

        Returns:
            Shadowstep: self instance for chaining.

        Raises:
            GeneralShadowstepException: if none of the strategies succeed.
        """
        self.logger.info(
            f"{inspect.currentframe().f_code.co_name} with args locator={locator}, x={x}, y={y}, image={bool(image)}")

        try:
            if locator:
                # If locator is already an Element or WebElement
                if isinstance(locator, Element):
                    locator.tap(duration=duration)
                elif isinstance(locator, WebElement):
                    # Wrap into our lazy Element and tap
                    elem = Element(locator=(), base=self)
                    elem._element = locator
                    elem.tap(duration=duration)
                else:
                    # Create lazy element from locator
                    self.get_element(locator=locator, timeout=int(timeout)).tap(duration=duration)
                return self

            elif x is not None and y is not None:
                # Use driver touch_action for coordinate tap
                self.logger.debug(f"Tapping at coordinates: ({x}, {y})")
                self.driver.tap([(x, y)], duration or 100)
                return self

            elif image:
                raise NotImplementedError(f"image {inspect.currentframe().f_code.co_name} is not yet implemented.")
                # # Handle different image input types
                # if isinstance(image, str):
                #     img_data = Image.open(image).convert("RGB")
                # elif isinstance(image, bytes):
                #     from io import BytesIO
                #     img_data = Image.open(BytesIO(image)).convert("RGB")
                # elif isinstance(image, np.ndarray):
                #     img_data = Image.fromarray(image)
                # elif isinstance(image, Image.Image):
                #     img_data = image.convert("RGB")
                # else:
                #     raise ValueError("Unsupported image format for tap.")
                #
                # from shadowstep.vision.image_matcher import find_image_on_screen  # предположим, что такой модуль есть
                #
                # coords = find_image_on_screen(
                #     driver=self.driver,
                #     template=img_data,
                #     threshold=threshold,
                #     timeout=timeout
                # )
                #
                # if coords:
                #     self.driver.tap([coords], duration or 100)
                #     return self
                #
                # raise GeneralShadowstepException("Image not found on screen.")

            else:
                raise GeneralShadowstepException("Tap requires locator, coordinates or image.")
        except Exception as e:
            self.logger.exception(f"Tap failed: {e}")
            raise GeneralShadowstepException(str(e)) from e

    def start_recording_screen(self) -> None:
        """Start screen recording using Appium driver."""
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            self.driver.start_recording_screen()
        except Exception as e:
            self.logger.exception("Failed to start screen recording")
            raise GeneralShadowstepException("start_recording_screen failed") from e

    def stop_recording_screen(self) -> bytes:
        """Stop screen recording and return video as bytes.

        Returns:
            bytes: Video recording in base64-decoded format.
        """
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            encoded = self.driver.stop_recording_screen()
            return base64.b64decode(encoded)
        except Exception as e:
            self.logger.exception("Failed to stop screen recording")
            raise GeneralShadowstepException("stop_recording_screen failed") from e

    def get_screenshot(self):
        self.logger.info(f"{inspect.currentframe().f_code.co_name}")
        try:
            return self.get_screenshot_as_base64_decoded()
        except Exception as e:
            self.logger.exception("Failed to get screenshot")
            raise GeneralShadowstepException("get_screenshot failed") from e


"""
self.driver.update_settings(settings={'enableMultiWindows': True})

https://github.com/appium/appium-uiautomator2-driver/blob/61abedddcde2d606394acfa0f0c2bac395a0e14c/README.md?plain=1#L304
## Settings API

UiAutomator2 driver supports Appium [Settings API](https://appium.io/docs/en/latest/guides/settings/).
Along with the common settings the following driver-specific settings are currently available:

Name | Type | Description
--- | --- | ---
actionAcknowledgmentTimeout | long | Maximum number of milliseconds to wait for an acknowledgment of generic uiautomator actions, such as clicks, text setting, and menu presses. The acknowledgment is an[AccessibilityEvent](http://developer.android.com/reference/android/view/accessibility/AccessibilityEvent.html") corresponding to an action, that lets the framework determine if the action was successful. Generally, this timeout should not be modified. `3000` ms by default
allowInvisibleElements | boolean | Whether to include elements that are not visible to the user (e. g. whose `displayed` attribute is `false`) to the XML source tree. `false` by default
ignoreUnimportantViews | boolean | Enables or disables layout hierarchy compression. If compression is enabled, the layout hierarchy derived from the Acessibility framework will only contain nodes that are important for uiautomator testing. Any unnecessary surrounding layout nodes that make viewing and searching the hierarchy inefficient are removed. `false` by default
elementResponseAttributes | string | Comma-separated list of element attribute names to be included into findElement response. By default only element UUID is present there, but it is also possible to add the following items: `name`, `text`, `rect`, `enabled`, `displayed`, `selected`, `attribute/<element_attribute_name>`. It is required that `shouldUseCompactResponses` setting is set to `false` in order for this one to apply.
enableMultiWindows | boolean | Whether to include all windows that the user can interact with (for example an on-screen keyboard) while building the XML page source (`true`). By default it is `false` and only the single active application window is included to the page source.
enableTopmostWindowFromActivePackage | boolean | Whether to limit the window with the highest Z-order from the active package for interactions and page source retrieval. By default it is `false` and the active application window, which may not necessarily have this order, is included to the page source.
enableNotificationListener | boolean | Whether to enable (`true`) toast notifications listener to listen for new toast notifications. By default this listener is enabled and UiAutomator2 server includes the text of toast messages to the generated XML page source, but not for longer than `3500` ms after the corresponding notification expires.
keyInjectionDelay | long | Delay in milliseconds between key presses when injecting text input. 0 ms by default
scrollAcknowledgmentTimeout | long | Timeout for waiting for an acknowledgement of an uiautomator scroll swipe action. The acknowledgment is an [AccessibilityEvent](http://developer.android.com/reference/android/view/accessibility/AccessibilityEvent.html), corresponding to the scroll action, that lets the framework determine if the scroll action was successful. Generally, this timeout should not be modified. `200` ms by default
shouldUseCompactResponses | boolean | Used in combination with `elementResponseAttributes` setting. If set to `false` then the findElement response is going to include the items enumerated in `elementResponseAttributes` setting. `true` by default
waitForIdleTimeout | long | Timeout used for waiting for the user interface to go into an idle state. By default, all core uiautomator objects except UiDevice will perform this wait before starting to search for the widget specified by the object's locator. Once the idle state is detected or the timeout elapses (whichever occurs first), the object will start to wait for the selector to find a match. Consider lowering the value of this setting if you experience long delays while interacting with accessibility elements in your test. `10000` ms by default.
waitForSelectorTimeout | long | Timeout for waiting for a widget to become visible in the user interface so that it can be matched by a selector. Because user interface content is dynamic, sometimes a widget may not be visible immediately and won't be detected by a selector. This timeout allows the uiautomator framework to wait for a match to be found, up until the timeout elapses. This timeout is only applied to `android uiautomator` location strategy. `10000` ms by default
normalizeTagNames | boolean | Being set to `true` applies unicode-to-ascii normalization of element class names used as tag names in the page source XML document. This is necessary if the application under test has some Unicode class names, which cannot be used as XML tag names by default due to known bugs in Android's XML DOM parser implementation. `false` by default
shutdownOnPowerDisconnect | boolean | Whether to shutdown the server if the device under test is disconnected from a power source (e. g. stays on battery power). `true` by default.
simpleBoundsCalculation | boolean | Whether to calculate element bounds as absolute values (`true`) or check if the element is covered by other elements and thus partially hidden (`false`, the default behaviour). Setting this setting to `true` helps to improve the performance of XML page source generation, but decreases bounds preciseness. Use with care.
trackScrollEvents | boolean | Whether to apply scroll events tracking (`true`, the default value), so the server could calculate the value of `contentSize` attribute. Having this setting enabled may add delays to all scrolling actions.
wakeLockTimeout | long | The timeout in milliseconds of wake lock that UiAutomator2 server acquires by default to prevent the device under test going to sleep while an automated test is running. By default the server acquires the lock for 24 hours. Setting this value to zero forces the server to release the wake lock.
serverPort | int | The number of the port on the remote device to start UiAutomator2 server on. Do not mix this with `systemPort`, which is acquired on the host machine. Must be in range 1024..65535. `6790` by default
mjpegServerPort | int | The number of the port on the remote device to start MJPEG screenshots broadcaster on. Must be in range 1024..65535. `7810` by default
mjpegServerFramerate | int | The maximum count of screenshots per second taken by the MJPEG screenshots broadcaster. Must be in range 1..60. `10` by default
mjpegScalingFactor | int | The percentage value used to apply downscaling on the screenshots generated by the MJPEG screenshots broadcaster. Must be in range 1..100. `50` is by default, which means that screenshots are downscaled to the half of their original size keeping their original proportions.
mjpegServerScreenshotQuality | int | The percentage value used to apply lossy JPEG compression on the screenshots generated by the MJPEG screenshots broadcaster. Must be in range 1..100. `50` is by default, which means that screenshots are compressed to the half of their original quality.
mjpegBilinearFiltering | boolean | Controls whether (`true`) or not (`false`, the default value) to apply bilinear filtering to MJPEG screenshots broadcaster resize algorithm. Enabling this flag may improve the quality of the resulting scaled bitmap, but may introduce a small performance hit.
useResourcesForOrientationDetection | boolean | Defines the strategy used by UiAutomator2 server to detect the original device orientation. By default (`false` value) the server uses device rotation value for this purpose. Although, this approach may not work for some devices and a portrait orientation may erroneously be detected as the landscape one (and vice versa). In such case it makes sense to play with this setting.
enforceXPath1 | boolean | Since UiAutomator2 driver version `4.25.0` XPath2 is set as the default and the recommended interpreter for the corresponding element locators. This interpreter is based on [Psychopath XPath2](https://wiki.eclipse.org/PsychoPathXPathProcessor) implementation, which is now a part of the Eclipse foundation. In most of the cases XPath1 locators are also valid XPath2 locators, so there should be no issues while locating elements. Although, since the XPath2 standard is much more advanced in comparison to the previous version, some [issues](https://github.com/appium/appium/issues/16142) are possible for more sophisticated locators, which cannot be fixed easily, as we depend on the third-party library mentioned above. Then try to workaround such issues by enforcing XPath1 usage (whose implementation is a part of the Android platform itself) and assigning this setting to `true`. Note, this setting is actually applied at the time when the element lookup by XPath is executed, so you could switch it on or off whenever needed throughout your automated testing session.
limitXPathContextScope | boolean | Due to historical reasons UiAutomator2 driver limits scopes of element context-based searches to the parent element. This means a request like `findElement(By.xpath, "//root").findElement(By.xpath, "./..")` would always fail, because the driver only collects descendants of the `root` element for the destination XML source. The `limitXPathContextScope` setting being set to `false` changes that default behavior, so the collected page source includes the whole page source XML where `root` node is set as the search context. With that setting disabled the search query above should not fail anymore. Although, you must still be careful while building XPath requests for context-based searches with the `limitXPathContextScope` setting set to `false`. A request like `findElement(By.xpath, "//root").findElement(By.xpath, "//element")` would ignore the current context and search for `element` trough the whole page source. Use `.` notation to correct that behavior and only find `element` nodes which are descendants of the `root` node: `findElement(By.xpath, "//root").findElement(By.xpath, ".//element")`.
disableIdLocatorAutocompletion | boolean | According to internal Android standards it is expected that each resource identifier is prefixed with `<packageName>:id/` string. This should guarantee uniqueness of each identifier. Although some application development frameworks ignore this rule and don't add such prefix automatically or, rather, let it up to the developer to decide how to represent their application identifiers. For example, [testTag modifier attribute in the Jetpack Compose](https://developer.android.com/reference/kotlin/androidx/compose/ui/platform/package-summary#(androidx.compose.ui.Modifier).testTag(kotlin.String)) with [testTagsAsResourceId](https://developer.android.com/reference/kotlin/androidx/compose/ui/semantics/package-summary#(androidx.compose.ui.semantics.SemanticsPropertyReceiver).testTagsAsResourceId()) allows developers to set an arbitrary string without the prefix rule. [Interoperability with UiAutomator](https://developer.android.com/jetpack/compose/testing) also explains how to set it. By default UIA2 driver adds the above prefixes automatically to all resource id locators if they are not prefixed, but in case of such "special" apps this feature might be disabled by assigning the setting to `true`.
includeExtrasInPageSource | boolean | Whether to include `extras` element attribute in the XML page source result. Then, XPath locator can find the element by the extras. Its value consists of combined [getExtras](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo#getExtras()) as `keys=value` pair separated by a semicolon (`;`), thus you may need to find the element with partial matching like `contains` e.g. `driver.find_element :xpath, '//*[contains(@extras, "AccessibilityNodeInfo.roleDescription=")]'`. The value could be huge if elements in the XML page source have large `extras`. It could affect the performance of XML page source generation.
includeA11yActionsInPageSource | boolean | Whether to include `actions` element attribute in the XML page source result. Its value consists of names of available accessibility actions from [getActionList](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo#getActionList()), separated by a comma. The value could be huge if elements in the XML page source have a lot of actions and could affect the performance of XML page source generation.
snapshotMaxDepth | int | The number of maximum depth for the source tree snapshot. The default value is `70`. This number should be in range [1, 500]. A part of the elements source tree might be lost if the value is too low. Also, StackOverflowError might be caused if the value is too high (Issues [12545](https://github.com/appium/appium/issues/12545), [12892](https://github.com/appium/appium/issues/12892)). The available driver version is `2.27.0` or higher.
currentDisplayId | int | The id of the display that should be used when finding elements, taking screenshots, etc. It can be found in the output of `adb shell dumpsys display` (search for `mDisplayId`). The default value is [Display.DEFAULT_DISPLAY](https://developer.android.com/reference/android/view/Display#DEFAULT_DISPLAY). **Please note that it is different from the physical display id, reported by `adb shell dumpsys SurfaceFlinger --display-id`**. **Additionally, please note that `-android uiautomator` (e.g., `UiSelector`) doesn't work predictably with multiple displays, as this is an Android limitation.** **Multi-display support is only available since Android R (30 API level).**


"""


