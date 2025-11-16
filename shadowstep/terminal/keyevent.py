# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

"""KeyEvent interface for Shadowstep framework.

This module provides the KeyEvent class for executing ADB commands
through Appium server, see:
https://developer.android.com/reference/android/view/KeyEvent
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shadowstep.terminal import Terminal

# Configure the root logger (basic configuration)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class KeyEvent:
    """Handles all key events from Android KeyEvent API.

    Provides methods for all Android key codes:
    - Navigation keys (DPAD_UP, DPAD_DOWN, etc.)
    - System keys (HOME, BACK, MENU, etc.)
    - Media keys (VOLUME_UP, VOLUME_DOWN, etc.)
    - Text input keys (ENTER, BACKSPACE, DELETE, etc.)
    - And all other keys from KeyEvent constants.
    """

    def __init__(self, terminal: "Terminal") -> None:
        """Initialize the TerminalCredentialsError.

        Args:
            terminal: Terminal instance.

        """
        self._terminal = terminal

    def press_home(self) -> bool:
        """Simulate pressing the home button on the device.

        :return: True if the home button press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_HOME")

    def press_0(self) -> bool:
        """Simulate pressing the 0 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_0")

    def press_1(self) -> bool:
        """Simulate pressing the 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_1")

    def press_2(self) -> bool:
        """Simulate pressing the 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_2")

    def press_3(self) -> bool:
        """Simulate pressing the 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_3")

    def press_4(self) -> bool:
        """Simulate pressing the 4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_4")

    def press_5(self) -> bool:
        """Simulate pressing the 5 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_5")

    def press_6(self) -> bool:
        """Simulate pressing the 6 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_6")

    def press_7(self) -> bool:
        """Simulate pressing the 7 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_7")

    def press_8(self) -> bool:
        """Simulate pressing the 8 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_8")

    def press_9(self) -> bool:
        """Simulate pressing the 9 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_9")

    def press_10(self) -> bool:
        """Simulate pressing the 10 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_10")

    def press_11(self) -> bool:
        """Simulate pressing the 11 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_11")

    def press_12(self) -> bool:
        """Simulate pressing the 12 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_12")

    def press_13(self) -> bool:
        """Simulate pressing the 13 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_13")

    def press_14(self) -> bool:
        """Simulate pressing the 14 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_14")

    def press_15(self) -> bool:
        """Simulate pressing the 15 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_15")

    def press_16(self) -> bool:
        """Simulate pressing the 16 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_16")

    def press_3d_mode(self) -> bool:
        """Simulate pressing the 3D mode key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_3D_MODE")

    def press_a(self) -> bool:
        """Simulate pressing the A key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_A")

    def press_all_apps(self) -> bool:
        """Simulate pressing the all apps key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ALL_APPS")

    def press_alt_left(self) -> bool:
        """Simulate pressing the left Alt key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ALT_LEFT")

    def press_alt_right(self) -> bool:
        """Simulate pressing the right Alt key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ALT_RIGHT")

    def press_apostrophe(self) -> bool:
        """Simulate pressing the apostrophe key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_APOSTROPHE")

    def press_app_switch(self) -> bool:
        """Simulate pressing the app switch key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_APP_SWITCH")

    def press_assist(self) -> bool:
        """Simulate pressing the assist key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ASSIST")

    def press_at(self) -> bool:
        """Simulate pressing the @ key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_AT")

    def press_avr_input(self) -> bool:
        """Simulate pressing the AVR input key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_AVR_INPUT")

    def press_avr_power(self) -> bool:
        """Simulate pressing the AVR power key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_AVR_POWER")

    def press_b(self) -> bool:
        """Simulate pressing the B key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_B")

    def press_back(self) -> bool:
        """Simulate pressing the back button on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BACK")

    def press_backslash(self) -> bool:
        """Simulate pressing the backslash key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BACKSLASH")

    def press_bookmark(self) -> bool:
        """Simulate pressing the bookmark key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BOOKMARK")

    def press_break(self) -> bool:
        """Simulate pressing the break key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BREAK")

    def press_brightness_down(self) -> bool:
        """Simulate pressing the brightness down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BRIGHTNESS_DOWN")

    def press_brightness_up(self) -> bool:
        """Simulate pressing the brightness up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BRIGHTNESS_UP")

    def press_button_1(self) -> bool:
        """Simulate pressing button 1 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_1")

    def press_button_2(self) -> bool:
        """Simulate pressing button 2 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_2")

    def press_button_3(self) -> bool:
        """Simulate pressing button 3 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_3")

    def press_button_4(self) -> bool:
        """Simulate pressing button 4 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_4")

    def press_button_5(self) -> bool:
        """Simulate pressing button 5 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_5")

    def press_button_6(self) -> bool:
        """Simulate pressing button 6 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_6")

    def press_button_7(self) -> bool:
        """Simulate pressing button 7 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_7")

    def press_button_8(self) -> bool:
        """Simulate pressing button 8 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_8")

    def press_button_9(self) -> bool:
        """Simulate pressing button 9 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_9")

    def press_button_10(self) -> bool:
        """Simulate pressing button 10 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_10")

    def press_button_11(self) -> bool:
        """Simulate pressing button 11 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_11")

    def press_button_12(self) -> bool:
        """Simulate pressing button 12 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_12")

    def press_button_13(self) -> bool:
        """Simulate pressing button 13 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_13")

    def press_button_14(self) -> bool:
        """Simulate pressing button 14 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_14")

    def press_button_15(self) -> bool:
        """Simulate pressing button 15 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_15")

    def press_button_16(self) -> bool:
        """Simulate pressing button 16 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_16")

    def press_button_a(self) -> bool:
        """Simulate pressing button A on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_A")

    def press_button_b(self) -> bool:
        """Simulate pressing button B on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_B")

    def press_button_c(self) -> bool:
        """Simulate pressing button C on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_C")

    def press_button_l1(self) -> bool:
        """Simulate pressing button L1 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_L1")

    def press_button_l2(self) -> bool:
        """Simulate pressing button L2 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_L2")

    def press_button_mode(self) -> bool:
        """Simulate pressing button mode on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_MODE")

    def press_button_r1(self) -> bool:
        """Simulate pressing button R1 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_R1")

    def press_button_r2(self) -> bool:
        """Simulate pressing button R2 on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_R2")

    def press_button_select(self) -> bool:
        """Simulate pressing button select on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_SELECT")

    def press_button_start(self) -> bool:
        """Simulate pressing button start on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_START")

    def press_button_thumbl(self) -> bool:
        """Simulate pressing button thumb left on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_THUMBL")

    def press_button_thumbr(self) -> bool:
        """Simulate pressing button thumb right on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_THUMBR")

    def press_button_x(self) -> bool:
        """Simulate pressing button X on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_X")

    def press_button_y(self) -> bool:
        """Simulate pressing button Y on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_Y")

    def press_button_z(self) -> bool:
        """Simulate pressing button Z on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_BUTTON_Z")

    def press_c(self) -> bool:
        """Simulate pressing the C key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_C")

    def press_calculator(self) -> bool:
        """Simulate pressing the calculator key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CALCULATOR")

    def press_calendar(self) -> bool:
        """Simulate pressing the calendar key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CALENDAR")

    def press_call(self) -> bool:
        """Simulate pressing the call key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CALL")

    def press_camera(self) -> bool:
        """Simulate pressing the camera key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CAMERA")

    def press_caps_lock(self) -> bool:
        """Simulate pressing the caps lock key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CAPS_LOCK")

    def press_captions(self) -> bool:
        """Simulate pressing the captions key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CAPTIONS")

    def press_channel_down(self) -> bool:
        """Simulate pressing the channel down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CHANNEL_DOWN")

    def press_channel_up(self) -> bool:
        """Simulate pressing the channel up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CHANNEL_UP")

    def press_clear(self) -> bool:
        """Simulate pressing the clear key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CLEAR")

    def press_close(self) -> bool:
        """Simulate pressing the close key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CLOSE")

    def press_comma(self) -> bool:
        """Simulate pressing the comma key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_COMMA")

    def press_contacts(self) -> bool:
        """Simulate pressing the contacts key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CONTACTS")

    def press_copy(self) -> bool:
        """Simulate pressing the copy key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_COPY")

    def press_ctrl_left(self) -> bool:
        """Simulate pressing the left Ctrl key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CTRL_LEFT")

    def press_ctrl_right(self) -> bool:
        """Simulate pressing the right Ctrl key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CTRL_RIGHT")

    def press_cut(self) -> bool:
        """Simulate pressing the cut key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_CUT")

    def press_d(self) -> bool:
        """Simulate pressing the D key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_D")

    def press_del(self) -> bool:
        """Simulate pressing the delete key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DEL")

    def press_demo_app_1(self) -> bool:
        """Simulate pressing the demo app 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DEMO_APP_1")

    def press_demo_app_2(self) -> bool:
        """Simulate pressing the demo app 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DEMO_APP_2")

    def press_demo_app_3(self) -> bool:
        """Simulate pressing the demo app 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DEMO_APP_3")

    def press_demo_app_4(self) -> bool:
        """Simulate pressing the demo app 4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DEMO_APP_4")

    def press_dictate(self) -> bool:
        """Simulate pressing the dictate key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DICTATE")

    def press_do_not_disturb(self) -> bool:
        """Simulate pressing the do not disturb key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DO_NOT_DISTURB")

    def press_dpad_center(self) -> bool:
        """Simulate pressing the D-pad center key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_CENTER")

    def press_dpad_down(self) -> bool:
        """Simulate pressing the D-pad down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_DOWN")

    def press_dpad_down_left(self) -> bool:
        """Simulate pressing the D-pad down-left key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_DOWN_LEFT")

    def press_dpad_down_right(self) -> bool:
        """Simulate pressing the D-pad down-right key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_DOWN_RIGHT")

    def press_dpad_left(self) -> bool:
        """Simulate pressing the D-pad left key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_LEFT")

    def press_dpad_right(self) -> bool:
        """Simulate pressing the D-pad right key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_RIGHT")

    def press_dpad_up(self) -> bool:
        """Simulate pressing the D-pad up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_UP")

    def press_dpad_up_left(self) -> bool:
        """Simulate pressing the D-pad up-left key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_UP_LEFT")

    def press_dpad_up_right(self) -> bool:
        """Simulate pressing the D-pad up-right key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DPAD_UP_RIGHT")

    def press_dvr(self) -> bool:
        """Simulate pressing the DVR key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_DVR")

    def press_e(self) -> bool:
        """Simulate pressing the E key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_E")

    def press_eisu(self) -> bool:
        """Simulate pressing the EISU key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_EISU")

    def press_emoji_picker(self) -> bool:
        """Simulate pressing the emoji picker key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_EMOJI_PICKER")

    def press_endcall(self) -> bool:
        """Simulate pressing the end call key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ENDCALL")

    def press_enter(self) -> bool:
        """Simulate pressing the enter key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ENTER")

    def press_envelope(self) -> bool:
        """Simulate pressing the envelope key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ENVELOPE")

    def press_equals(self) -> bool:
        """Simulate pressing the equals key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_EQUALS")

    def press_escape(self) -> bool:
        """Simulate pressing the escape key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ESCAPE")

    def press_explorer(self) -> bool:
        """Simulate pressing the explorer key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_EXPLORER")

    def press_f(self) -> bool:
        """Simulate pressing the F key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F")

    def press_f1(self) -> bool:
        """Simulate pressing the F1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F1")

    def press_f2(self) -> bool:
        """Simulate pressing the F2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F2")

    def press_f3(self) -> bool:
        """Simulate pressing the F3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F3")

    def press_f4(self) -> bool:
        """Simulate pressing the F4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F4")

    def press_f5(self) -> bool:
        """Simulate pressing the F5 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F5")

    def press_f6(self) -> bool:
        """Simulate pressing the F6 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F6")

    def press_f7(self) -> bool:
        """Simulate pressing the F7 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F7")

    def press_f8(self) -> bool:
        """Simulate pressing the F8 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F8")

    def press_f9(self) -> bool:
        """Simulate pressing the F9 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F9")

    def press_f10(self) -> bool:
        """Simulate pressing the F10 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F10")

    def press_f11(self) -> bool:
        """Simulate pressing the F11 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F11")

    def press_f12(self) -> bool:
        """Simulate pressing the F12 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F12")

    def press_f13(self) -> bool:
        """Simulate pressing the F13 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F13")

    def press_f14(self) -> bool:
        """Simulate pressing the F14 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F14")

    def press_f15(self) -> bool:
        """Simulate pressing the F15 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F15")

    def press_f16(self) -> bool:
        """Simulate pressing the F16 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F16")

    def press_f17(self) -> bool:
        """Simulate pressing the F17 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F17")

    def press_f18(self) -> bool:
        """Simulate pressing the F18 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F18")

    def press_f19(self) -> bool:
        """Simulate pressing the F19 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F19")

    def press_f20(self) -> bool:
        """Simulate pressing the F20 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F20")

    def press_f21(self) -> bool:
        """Simulate pressing the F21 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F21")

    def press_f22(self) -> bool:
        """Simulate pressing the F22 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F22")

    def press_f23(self) -> bool:
        """Simulate pressing the F23 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F23")

    def press_f24(self) -> bool:
        """Simulate pressing the F24 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_F24")

    def press_featured_app_1(self) -> bool:
        """Simulate pressing the featured app 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FEATURED_APP_1")

    def press_featured_app_2(self) -> bool:
        """Simulate pressing the featured app 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FEATURED_APP_2")

    def press_featured_app_3(self) -> bool:
        """Simulate pressing the featured app 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FEATURED_APP_3")

    def press_featured_app_4(self) -> bool:
        """Simulate pressing the featured app 4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FEATURED_APP_4")

    def press_focus(self) -> bool:
        """Simulate pressing the focus key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FOCUS")

    def press_forward(self) -> bool:
        """Simulate pressing the forward key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FORWARD")

    def press_forward_del(self) -> bool:
        """Simulate pressing the forward delete key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FORWARD_DEL")

    def press_fullscreen(self) -> bool:
        """Simulate pressing the fullscreen key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FULLSCREEN")

    def press_function(self) -> bool:
        """Simulate pressing the function key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_FUNCTION")

    def press_g(self) -> bool:
        """Simulate pressing the G key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_G")

    def press_grave(self) -> bool:
        """Simulate pressing the grave key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_GRAVE")

    def press_guide(self) -> bool:
        """Simulate pressing the guide key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_GUIDE")

    def press_h(self) -> bool:
        """Simulate pressing the H key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_H")

    def press_headset_hook(self) -> bool:
        """Simulate pressing the headset hook key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_HEADSETHOOK")

    def press_help(self) -> bool:
        """Simulate pressing the help key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_HELP")

    def press_henkan(self) -> bool:
        """Simulate pressing the henkan key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_HENKAN")

    def press_i(self) -> bool:
        """Simulate pressing the I key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_I")

    def press_info(self) -> bool:
        """Simulate pressing the info key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_INFO")

    def press_insert(self) -> bool:
        """Simulate pressing the insert key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_INSERT")

    def press_j(self) -> bool:
        """Simulate pressing the J key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_J")

    def press_k(self) -> bool:
        """Simulate pressing the K key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_K")

    def press_kana(self) -> bool:
        """Simulate pressing the kana key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_KANA")

    def press_katakana_hiragana(self) -> bool:
        """Simulate pressing the katakana hiragana key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_KATAKANA_HIRAGANA")

    def press_keyboard_backlight_down(self) -> bool:
        """Simulate pressing the keyboard backlight down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_KEYBOARD_BACKLIGHT_DOWN")

    def press_keyboard_backlight_toggle(self) -> bool:
        """Simulate pressing the keyboard backlight toggle key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_KEYBOARD_BACKLIGHT_TOGGLE")

    def press_keyboard_backlight_up(self) -> bool:
        """Simulate pressing the keyboard backlight up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_KEYBOARD_BACKLIGHT_UP")

    def press_l(self) -> bool:
        """Simulate pressing the L key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_L")

    def press_language_switch(self) -> bool:
        """Simulate pressing the language switch key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_LANGUAGE_SWITCH")

    def press_last_channel(self) -> bool:
        """Simulate pressing the last channel key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_LAST_CHANNEL")

    def press_left_bracket(self) -> bool:
        """Simulate pressing the left bracket key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_LEFT_BRACKET")

    def press_lock(self) -> bool:
        """Simulate pressing the lock key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_LOCK")

    def press_m(self) -> bool:
        """Simulate pressing the M key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_M")

    def press_macro_1(self) -> bool:
        """Simulate pressing the macro 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MACRO_1")

    def press_macro_2(self) -> bool:
        """Simulate pressing the macro 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MACRO_2")

    def press_macro_3(self) -> bool:
        """Simulate pressing the macro 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MACRO_3")

    def press_macro_4(self) -> bool:
        """Simulate pressing the macro 4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MACRO_4")

    def press_manner_mode(self) -> bool:
        """Simulate pressing the manner mode key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MANNER_MODE")

    def press_media_audio_track(self) -> bool:
        """Simulate pressing the media audio track key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_AUDIO_TRACK")

    def press_media_close(self) -> bool:
        """Simulate pressing the media close key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_CLOSE")

    def press_media_eject(self) -> bool:
        """Simulate pressing the media eject key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_EJECT")

    def press_media_fast_forward(self) -> bool:
        """Simulate pressing the media fast forward key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_FAST_FORWARD")

    def press_media_next(self) -> bool:
        """Simulate pressing the media next key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_NEXT")

    def press_media_pause(self) -> bool:
        """Simulate pressing the media pause key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_PAUSE")

    def press_media_play(self) -> bool:
        """Simulate pressing the media play key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_PLAY")

    def press_media_play_pause(self) -> bool:
        """Simulate pressing the media play/pause key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_PLAY_PAUSE")

    def press_media_previous(self) -> bool:
        """Simulate pressing the media previous key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_PREVIOUS")

    def press_media_record(self) -> bool:
        """Simulate pressing the media record key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_RECORD")

    def press_media_rewind(self) -> bool:
        """Simulate pressing the media rewind key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_REWIND")

    def press_media_skip_backward(self) -> bool:
        """Simulate pressing the media skip backward key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_SKIP_BACKWARD")

    def press_media_skip_forward(self) -> bool:
        """Simulate pressing the media skip forward key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_SKIP_FORWARD")

    def press_media_step_backward(self) -> bool:
        """Simulate pressing the media step backward key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_STEP_BACKWARD")

    def press_media_step_forward(self) -> bool:
        """Simulate pressing the media step forward key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_STEP_FORWARD")

    def press_media_stop(self) -> bool:
        """Simulate pressing the media stop key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_STOP")

    def press_media_top_menu(self) -> bool:
        """Simulate pressing the media top menu key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MEDIA_TOP_MENU")

    def press_menu(self) -> bool:
        """Simulate pressing the menu key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MENU")

    def press_meta_left(self) -> bool:
        """Simulate pressing the left meta key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_META_LEFT")

    def press_meta_right(self) -> bool:
        """Simulate pressing the right meta key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_META_RIGHT")

    def press_minus(self) -> bool:
        """Simulate pressing the minus key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MINUS")

    def press_move_end(self) -> bool:
        """Simulate pressing the move end key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MOVE_END")

    def press_move_home(self) -> bool:
        """Simulate pressing the move home key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MOVE_HOME")

    def press_muhenkan(self) -> bool:
        """Simulate pressing the muhenkan key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MUHENKAN")

    def press_music(self) -> bool:
        """Simulate pressing the music key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MUSIC")

    def press_mute(self) -> bool:
        """Simulate pressing the mute key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_MUTE")

    def press_n(self) -> bool:
        """Simulate pressing the N key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_N")

    def press_navigate_in(self) -> bool:
        """Simulate pressing the navigate in key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NAVIGATE_IN")

    def press_navigate_next(self) -> bool:
        """Simulate pressing the navigate next key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NAVIGATE_NEXT")

    def press_navigate_out(self) -> bool:
        """Simulate pressing the navigate out key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NAVIGATE_OUT")

    def press_navigate_previous(self) -> bool:
        """Simulate pressing the navigate previous key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NAVIGATE_PREVIOUS")

    def press_new(self) -> bool:
        """Simulate pressing the new key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NEW")

    def press_notification(self) -> bool:
        """Simulate pressing the notification key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NOTIFICATION")

    def press_num(self) -> bool:
        """Simulate pressing the num key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUM")

    def press_numpad_0(self) -> bool:
        """Simulate pressing the numpad 0 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_0")

    def press_numpad_1(self) -> bool:
        """Simulate pressing the numpad 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_1")

    def press_numpad_2(self) -> bool:
        """Simulate pressing the numpad 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_2")

    def press_numpad_3(self) -> bool:
        """Simulate pressing the numpad 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_3")

    def press_numpad_4(self) -> bool:
        """Simulate pressing the numpad 4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_4")

    def press_numpad_5(self) -> bool:
        """Simulate pressing the numpad 5 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_5")

    def press_numpad_6(self) -> bool:
        """Simulate pressing the numpad 6 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_6")

    def press_numpad_7(self) -> bool:
        """Simulate pressing the numpad 7 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_7")

    def press_numpad_8(self) -> bool:
        """Simulate pressing the numpad 8 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_8")

    def press_numpad_9(self) -> bool:
        """Simulate pressing the numpad 9 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_9")

    def press_numpad_add(self) -> bool:
        """Simulate pressing the numpad add key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_ADD")

    def press_numpad_comma(self) -> bool:
        """Simulate pressing the numpad comma key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_COMMA")

    def press_numpad_divide(self) -> bool:
        """Simulate pressing the numpad divide key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_DIVIDE")

    def press_numpad_dot(self) -> bool:
        """Simulate pressing the numpad dot key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_DOT")

    def press_numpad_enter(self) -> bool:
        """Simulate pressing the numpad enter key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_ENTER")

    def press_numpad_equals(self) -> bool:
        """Simulate pressing the numpad equals key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_EQUALS")

    def press_numpad_left_paren(self) -> bool:
        """Simulate pressing the numpad left parenthesis key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_LEFT_PAREN")

    def press_numpad_multiply(self) -> bool:
        """Simulate pressing the numpad multiply key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_MULTIPLY")

    def press_numpad_right_paren(self) -> bool:
        """Simulate pressing the numpad right parenthesis key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_RIGHT_PAREN")

    def press_numpad_subtract(self) -> bool:
        """Simulate pressing the numpad subtract key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUMPAD_SUBTRACT")

    def press_num_lock(self) -> bool:
        """Simulate pressing the num lock key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_NUM_LOCK")

    def press_o(self) -> bool:
        """Simulate pressing the O key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_O")

    def press_p(self) -> bool:
        """Simulate pressing the P key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_P")

    def press_page_down(self) -> bool:
        """Simulate pressing the page down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PAGE_DOWN")

    def press_page_up(self) -> bool:
        """Simulate pressing the page up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PAGE_UP")

    def press_pairing(self) -> bool:
        """Simulate pressing the pairing key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PAIRING")

    def press_paste(self) -> bool:
        """Simulate pressing the paste key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PASTE")

    def press_period(self) -> bool:
        """Simulate pressing the period key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PERIOD")

    def press_pictsymbols(self) -> bool:
        """Simulate pressing the pict symbols key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PICTSYMBOLS")

    def press_plus(self) -> bool:
        """Simulate pressing the plus key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PLUS")

    def press_pound(self) -> bool:
        """Simulate pressing the pound key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_POUND")

    def press_power(self) -> bool:
        """Simulate pressing the power key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_POWER")

    def press_print(self) -> bool:
        """Simulate pressing the print key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PRINT")

    def press_profile_switch(self) -> bool:
        """Simulate pressing the profile switch key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PROFILE_SWITCH")

    def press_prog_blue(self) -> bool:
        """Simulate pressing the prog blue key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PROG_BLUE")

    def press_prog_green(self) -> bool:
        """Simulate pressing the prog green key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PROG_GREEN")

    def press_prog_red(self) -> bool:
        """Simulate pressing the prog red key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PROG_RED")

    def press_prog_yellow(self) -> bool:
        """Simulate pressing the prog yellow key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_PROG_YELLOW")

    def press_q(self) -> bool:
        """Simulate pressing the Q key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_Q")

    def press_r(self) -> bool:
        """Simulate pressing the R key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_R")

    def press_recent_apps(self) -> bool:
        """Simulate pressing the recent apps key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_RECENT_APPS")

    def press_refresh(self) -> bool:
        """Simulate pressing the refresh key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_REFRESH")

    def press_right_bracket(self) -> bool:
        """Simulate pressing the right bracket key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_RIGHT_BRACKET")

    def press_ro(self) -> bool:
        """Simulate pressing the RO key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_RO")

    def press_s(self) -> bool:
        """Simulate pressing the S key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_S")

    def press_screenshot(self) -> bool:
        """Simulate pressing the screenshot key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SCREENSHOT")

    def press_scroll_lock(self) -> bool:
        """Simulate pressing the scroll lock key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SCROLL_LOCK")

    def press_search(self) -> bool:
        """Simulate pressing the search key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SEARCH")

    def press_semicolon(self) -> bool:
        """Simulate pressing the semicolon key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SEMICOLON")

    def press_settings(self) -> bool:
        """Simulate pressing the settings key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SETTINGS")

    def press_shift_left(self) -> bool:
        """Simulate pressing the left shift key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SHIFT_LEFT")

    def press_shift_right(self) -> bool:
        """Simulate pressing the right shift key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SHIFT_RIGHT")

    def press_slash(self) -> bool:
        """Simulate pressing the slash key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SLASH")

    def press_sleep(self) -> bool:
        """Simulate pressing the sleep key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SLEEP")

    def press_soft_left(self) -> bool:
        """Simulate pressing the soft left key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SOFT_LEFT")

    def press_soft_right(self) -> bool:
        """Simulate pressing the soft right key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SOFT_RIGHT")

    def press_soft_sleep(self) -> bool:
        """Simulate pressing the soft sleep key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SOFT_SLEEP")

    def press_space(self) -> bool:
        """Simulate pressing the space key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SPACE")

    def press_star(self) -> bool:
        """Simulate pressing the star key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STAR")

    def press_stb_input(self) -> bool:
        """Simulate pressing the STB input key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STB_INPUT")

    def press_stb_power(self) -> bool:
        """Simulate pressing the STB power key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STB_POWER")

    def press_stem_1(self) -> bool:
        """Simulate pressing the stem 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STEM_1")

    def press_stem_2(self) -> bool:
        """Simulate pressing the stem 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STEM_2")

    def press_stem_3(self) -> bool:
        """Simulate pressing the stem 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STEM_3")

    def press_stem_primary(self) -> bool:
        """Simulate pressing the stem primary key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STEM_PRIMARY")

    def press_stylus_button_primary(self) -> bool:
        """Simulate pressing the stylus button primary key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STYLUS_BUTTON_PRIMARY")

    def press_stylus_button_secondary(self) -> bool:
        """Simulate pressing the stylus button secondary key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STYLUS_BUTTON_SECONDARY")

    def press_stylus_button_tail(self) -> bool:
        """Simulate pressing the stylus button tail key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STYLUS_BUTTON_TAIL")

    def press_stylus_button_tertiary(self) -> bool:
        """Simulate pressing the stylus button tertiary key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_STYLUS_BUTTON_TERTIARY")

    def press_switch_charset(self) -> bool:
        """Simulate pressing the switch charset key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SWITCH_CHARSET")

    def press_sym(self) -> bool:
        """Simulate pressing the sym key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SYM")

    def press_sysrq(self) -> bool:
        """Simulate pressing the sysrq key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SYSRQ")

    def press_system_navigation_down(self) -> bool:
        """Simulate pressing the system navigation down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SYSTEM_NAVIGATION_DOWN")

    def press_system_navigation_left(self) -> bool:
        """Simulate pressing the system navigation left key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SYSTEM_NAVIGATION_LEFT")

    def press_system_navigation_right(self) -> bool:
        """Simulate pressing the system navigation right key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SYSTEM_NAVIGATION_RIGHT")

    def press_system_navigation_up(self) -> bool:
        """Simulate pressing the system navigation up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_SYSTEM_NAVIGATION_UP")

    def press_t(self) -> bool:
        """Simulate pressing the T key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_T")

    def press_tab(self) -> bool:
        """Simulate pressing the tab key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TAB")

    def press_thumbs_down(self) -> bool:
        """Simulate pressing the thumbs down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_THUMBS_DOWN")

    def press_thumbs_up(self) -> bool:
        """Simulate pressing the thumbs up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_THUMBS_UP")

    def press_tv(self) -> bool:
        """Simulate pressing the TV key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV")

    def press_tv_antenna_cable(self) -> bool:
        """Simulate pressing the TV antenna cable key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_ANTENNA_CABLE")

    def press_tv_audio_description(self) -> bool:
        """Simulate pressing the TV audio description key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_AUDIO_DESCRIPTION")

    def press_tv_audio_description_mix_down(self) -> bool:
        """Simulate pressing the TV audio description mix down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_AUDIO_DESCRIPTION_MIX_DOWN")

    def press_tv_audio_description_mix_up(self) -> bool:
        """Simulate pressing the TV audio description mix up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_AUDIO_DESCRIPTION_MIX_UP")

    def press_tv_contents_menu(self) -> bool:
        """Simulate pressing the TV contents menu key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_CONTENTS_MENU")

    def press_tv_data_service(self) -> bool:
        """Simulate pressing the TV data service key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_DATA_SERVICE")

    def press_tv_input(self) -> bool:
        """Simulate pressing the TV input key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT")

    def press_tv_input_component_1(self) -> bool:
        """Simulate pressing the TV input component 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_COMPONENT_1")

    def press_tv_input_component_2(self) -> bool:
        """Simulate pressing the TV input component 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_COMPONENT_2")

    def press_tv_input_composite_1(self) -> bool:
        """Simulate pressing the TV input composite 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_COMPOSITE_1")

    def press_tv_input_composite_2(self) -> bool:
        """Simulate pressing the TV input composite 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_COMPOSITE_2")

    def press_tv_input_hdmi_1(self) -> bool:
        """Simulate pressing the TV input HDMI 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_HDMI_1")

    def press_tv_input_hdmi_2(self) -> bool:
        """Simulate pressing the TV input HDMI 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_HDMI_2")

    def press_tv_input_hdmi_3(self) -> bool:
        """Simulate pressing the TV input HDMI 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_HDMI_3")

    def press_tv_input_hdmi_4(self) -> bool:
        """Simulate pressing the TV input HDMI 4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_HDMI_4")

    def press_tv_input_vga_1(self) -> bool:
        """Simulate pressing the TV input VGA 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_INPUT_VGA_1")

    def press_tv_media_context_menu(self) -> bool:
        """Simulate pressing the TV media context menu key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_MEDIA_CONTEXT_MENU")

    def press_tv_network(self) -> bool:
        """Simulate pressing the TV network key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_NETWORK")

    def press_tv_number_entry(self) -> bool:
        """Simulate pressing the TV number entry key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_NUMBER_ENTRY")

    def press_tv_power(self) -> bool:
        """Simulate pressing the TV power key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_POWER")

    def press_tv_radio_service(self) -> bool:
        """Simulate pressing the TV radio service key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_RADIO_SERVICE")

    def press_tv_satellite(self) -> bool:
        """Simulate pressing the TV satellite key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_SATELLITE")

    def press_tv_satellite_bs(self) -> bool:
        """Simulate pressing the TV satellite BS key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_SATELLITE_BS")

    def press_tv_satellite_cs(self) -> bool:
        """Simulate pressing the TV satellite CS key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_SATELLITE_CS")

    def press_tv_satellite_service(self) -> bool:
        """Simulate pressing the TV satellite service key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_SATELLITE_SERVICE")

    def press_tv_teletex(self) -> bool:
        """Simulate pressing the TV teletext key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_TELETEXT")

    def press_tv_terrestrial_analog(self) -> bool:
        """Simulate pressing the TV terrestrial analog key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_TERRESTRIAL_ANALOG")

    def press_tv_terrestrial_digital(self) -> bool:
        """Simulate pressing the TV terrestrial digital key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_TERRESTRIAL_DIGITAL")

    def press_tv_timer_programming(self) -> bool:
        """Simulate pressing the TV timer programming key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_TIMER_PROGRAMMING")

    def press_tv_zoom_mode(self) -> bool:
        """Simulate pressing the TV zoom mode key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_TV_ZOOM_MODE")

    def press_u(self) -> bool:
        """Simulate pressing the U key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_U")

    def press_unknown(self) -> bool:
        """Simulate pressing the unknown key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_UNKNOWN")

    def press_v(self) -> bool:
        """Simulate pressing the V key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_V")

    def press_video_app_1(self) -> bool:
        """Simulate pressing the video app 1 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_1")

    def press_video_app_2(self) -> bool:
        """Simulate pressing the video app 2 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_2")

    def press_video_app_3(self) -> bool:
        """Simulate pressing the video app 3 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_3")

    def press_video_app_4(self) -> bool:
        """Simulate pressing the video app 4 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_4")

    def press_video_app_5(self) -> bool:
        """Simulate pressing the video app 5 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_5")

    def press_video_app_6(self) -> bool:
        """Simulate pressing the video app 6 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_6")

    def press_video_app_7(self) -> bool:
        """Simulate pressing the video app 7 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_7")

    def press_video_app_8(self) -> bool:
        """Simulate pressing the video app 8 key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VIDEO_APP_8")

    def press_voice_assist(self) -> bool:
        """Simulate pressing the voice assist key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VOICE_ASSIST")

    def press_volume_down(self) -> bool:
        """Simulate pressing the volume down key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VOLUME_DOWN")

    def press_volume_mute(self) -> bool:
        """Simulate pressing the volume mute key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VOLUME_MUTE")

    def press_volume_up(self) -> bool:
        """Simulate pressing the volume up key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_VOLUME_UP")

    def press_w(self) -> bool:
        """Simulate pressing the W key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_W")

    def press_wakeup(self) -> bool:
        """Simulate pressing the wakeup key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_WAKEUP")

    def press_window(self) -> bool:
        """Simulate pressing the window key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_WINDOW")

    def press_x(self) -> bool:
        """Simulate pressing the X key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_X")

    def press_y(self) -> bool:
        """Simulate pressing the Y key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_Y")

    def press_yen(self) -> bool:
        """Simulate pressing the yen key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_YEN")

    def press_z(self) -> bool:
        """Simulate pressing the Z key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_Z")

    def press_zenkaku_hankaku(self) -> bool:
        """Simulate pressing the zenkaku hankaku key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ZENKAKU_HANKAKU")

    def press_zoom_in(self) -> bool:
        """Simulate pressing the zoom in key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ZOOM_IN")

    def press_zoom_out(self) -> bool:
        """Simulate pressing the zoom out key on the device.

        :return: True if the key press was successfully simulated, False otherwise.
        """
        return self._terminal.input_keycode(keycode="KEYCODE_ZOOM_OUT")
