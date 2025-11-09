# Mobile Commands Reference

Shadowstep delegates mobile-specific commands to the Appium UIAutomator2 driver. Use the following official resources to explore the full API surface:

- [Driver overview](https://github.com/appium/appium-uiautomator2-driver)
- [Android mobile gestures](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md)
- [Files management](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#files-management)
- [Clipboard management](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#clipboard-management)

## Frequently Used Commands

- `mobile: shell` — [Run shell commands](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-shell)
- `mobile: scroll` — [Scroll a container](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scroll)
- `mobile: scrollGesture` — [Perform a scroll gesture](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-scrollgesture)
- `mobile: swipeGesture` — [Perform a swipe gesture](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-swipegesture)
- `mobile: clickGesture` — [Tap on coordinates or elements](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-clickgesture)
- `mobile: dragGesture` — [Drag elements across the screen](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-draggesture)
- `mobile: pinchOpenGesture` — [Zoom in](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchopengesture)
- `mobile: pinchCloseGesture` — [Zoom out](https://github.com/appium/appium-uiautomator2-driver/blob/master/docs/android-mobile-gestures.md#mobile-pinchclosegesture)
- `mobile: deepLink` — [Open deep links](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deeplink)
- `mobile: startLogsBroadcast` / `mobile: stopLogsBroadcast` — [Stream logcat events](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startlogsbroadcast)
- `mobile: getNotifications` / `mobile: openNotifications` — [Interact with notifications](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getnotifications)
- `mobile: batteryInfo` — [Inspect device battery state](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-batteryinfo)
- `mobile: changePermissions` — [Update app permissions](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-changepermissions)
- `mobile: startScreenStreaming` / `mobile: stopScreenStreaming` — [Manage screen recording](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startscreenstreaming)
- `mobile: scheduleAction` / `mobile: unscheduleAction` — [Manage scheduled actions](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-scheduleaction)
- `mobile: getActionHistory` — [Inspect scheduled action history](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getactionhistory)
- `mobile: installApp` / `mobile: removeApp` / `mobile: activateApp` — [Application lifecycle](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-installapp)
- `mobile: getConnectivity` / `mobile: setConnectivity` — [Network toggles](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-getconnectivity)
- `mobile: setUiMode` / `mobile: getUiMode` — [Manage UI mode](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setuimode)
- `mobile: setClipboard` / `mobile: getClipboard` — [Clipboard utilities](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-setclipboard)
- `mobile: pullFile` / `mobile: pushFile` — [File transfer](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-pullfile)

Review the upstream documentation for the exhaustive list of commands, required arguments, and usage nuances. Keep this summary in sync with the driver capabilities shipped in the version pinned in `uv.lock`.
