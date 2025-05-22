import inspect

from typing import Union, Dict, List

from appium.webdriver.common.mobileby import MobileBy

from selenium.common.exceptions import NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepException

from shadowstep.utils.decorators import fail_safe

from shadowstep.base import WebDriverSingleton



class ShadowstepMobileCommandsMixin:

    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def activate_app(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile activateapp
        Execute mobile: activateApp command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: activateApp', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def batteryinfo(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile batteryinfo
        Execute mobile: batteryInfo command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: batteryInfo', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def clearelement(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile clearelement
        Execute mobile: clearElement command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: clearElement', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def deviceinfo(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile deviceinfo
        Execute mobile: deviceInfo command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: deviceInfo', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def fingerprint(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile fingerprint
        Execute mobile: fingerprint command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: fingerprint', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_clipboard(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile getclipboard
        Execute mobile: getClipboard command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getClipboard', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_current_activity(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile getcurrentactivity
        Execute mobile: getCurrentActivity command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getCurrentActivity', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_currentpackage(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile getcurrentpackage
        Execute mobile: getCurrentPackage command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getCurrentPackage', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_devicetime(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile getdevicetime
        Execute mobile: getDeviceTime command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getDeviceTime', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_performancedata(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile getperformancedata
        Execute mobile: getPerformanceData command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getPerformanceData', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_performancedatatypes(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile getperformancedatatypes
        Execute mobile: getPerformanceDataTypes command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getPerformanceDataTypes', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_settings(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile getsettings
        Execute mobile: getSettings command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getSettings', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def hide_keyboard(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile hidekeyboard
        Execute mobile: hideKeyboard command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: hideKeyboard', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def install_app(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile installapp
        Execute mobile: installApp command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: installApp', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def is_appinstalled(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile isappinstalled
        Execute mobile: isAppInstalled command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: isAppInstalled', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def longpress_key(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile longpresskey
        Execute mobile: longPressKey command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: longPressKey', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def open_notifications(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile opennotifications
        Execute mobile: openNotifications command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: openNotifications', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def open_settings(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile opensettings
        Execute mobile: openSettings command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: openSettings', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def press_key(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile presskey
        Execute mobile: pressKey command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: pressKey', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def query_appstate(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile queryappstate
        Execute mobile: queryAppState command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: queryAppState', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def remove_app(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile removeapp
        Execute mobile: removeApp command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: removeApp', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def replaceelementvalue(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile replaceelementvalue
        Execute mobile: replaceElementValue command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: replaceElementValue', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def scroll_back_to(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile scrollbackto
        Execute mobile: scrollBackTo command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: scrollBackTo', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def send_sms(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile sendsms
        Execute mobile: sendSMS command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: sendSMS', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def set_clipboard(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile setclipboard
        Execute mobile: setClipboard command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: setClipboard', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def set_text(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile settext
        Execute mobile: setText command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: setText', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def shell(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile shell
        Execute mobile: shell command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: shell', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def start_activity(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile startactivity
        Execute mobile: startActivity command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: startActivity', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def start_logsbroadcast(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile startlogsbroadcast
        Execute mobile: startLogsBroadcast command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: startLogsBroadcast', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def stop_logsbroadcast(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile stoplogsbroadcast
        Execute mobile: stopLogsBroadcast command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: stopLogsBroadcast', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def terminate_app(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile terminateapp
        Execute mobile: terminateApp command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: terminateApp', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def togglelocationservices(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile togglelocationservices
        Execute mobile: toggleLocationServices command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: toggleLocationServices', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def update_settings(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile updatesettings
        Execute mobile: updateSettings command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: updateSettings', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def get_text(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile gettext
        Execute mobile: getText command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: getText', params or {})
        return self


    @fail_safe(
        retries=3,
        delay=0.5,
        raise_exception=ShadowstepException,
        exceptions=(NoSuchDriverException, InvalidSessionIdException, StaleElementReferenceException)
    )
    def performeditoraction(self, params: Union[Dict, List] = None) -> 'Shadowstep':
        """
        https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile performeditoraction
        Execute mobile: performEditorAction command.

        Args:
            params (Union[Dict, List]): Parameters for the mobile command.

        Returns:
            Shadowstep: Self for method chaining.
        """
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")
        self.driver = WebDriverSingleton.get_driver()
        self._execute('mobile: performEditorAction', params or {})
        return self

