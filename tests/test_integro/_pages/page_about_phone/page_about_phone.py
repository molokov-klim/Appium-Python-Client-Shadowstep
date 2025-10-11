# ruff: noqa
# pyright: ignore
import logging
from typing import Any
from shadowstep.decorators.common_decorators import current_page, log_info
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageAboutPhone(PageBaseShadowstep):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Any]:
        return {"PageSettings": self.to_back, "PageAndroidVersion": self.to_android_version}

    @property
    def name(self) -> str:
        return "About phone"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element(
            {
                "content-desc": "About phone",
                "resource-id": "com.android.settings:id/collapsing_toolbar",
                "class": "android.widget.FrameLayout",
            }
        )

    @log_info()
    def to_back(self):
        self.navigate_up.tap()
        return self.shadowstep.get_page("PageSettings")

    @log_info()
    def to_android_version(self):
        self.android_version.tap()
        return self.shadowstep.get_page("PageAndroidVersion")

    @property
    def navigate_up(self) -> Element:
        return self.recycler.scroll_to_element(
            {"content-desc": "Navigate up", "class": "android.widget.ImageButton"}
        )

    @property
    def basic_info(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Basic info",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def entity_header(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "resource-id": "com.android.settings:id/entity_header",
                "class": "android.widget.RelativeLayout",
            }
        )

    @property
    def entity_header_content(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "resource-id": "com.android.settings:id/entity_header_content",
                "class": "android.widget.LinearLayout",
            }
        )

    @property
    def owner(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Owner",
                "resource-id": "com.android.settings:id/entity_header_title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def legal_regulatory(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Legal & regulatory",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def legal_information(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Legal information",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def device_details(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Device details",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def device_name(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Device name",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def device_name_summary(self) -> Element:
        return self.device_name.get_sibling({"resource-id": "android:id/summary"})

    @property
    def phone_number(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Phone number",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def phone_number_summary(self) -> Element:
        return self.phone_number.get_sibling({"resource-id": "android:id/summary"})

    @property
    def android_version(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Android version",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def sim_status(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "SIM status",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def sim_status_summary(self) -> Element:
        return self.sim_status.get_sibling({"resource-id": "android:id/summary"})

    @property
    def model(self) -> Element:
        return self.recycler.scroll_to_element(
            {"text": "Model", "resource-id": "android:id/title", "class": "android.widget.TextView"}
        )

    @property
    def model_summary(self) -> Element:
        return self.model.get_sibling({"resource-id": "android:id/summary"})

    @property
    def imei(self) -> Element:
        return self.recycler.scroll_to_element(
            {"text": "IMEI", "resource-id": "android:id/title", "class": "android.widget.TextView"}
        )

    @property
    def imei_summary(self) -> Element:
        return self.imei.get_sibling({"resource-id": "android:id/summary"})

    @property
    def device_identifiers(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Device identifiers",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def wi_fi_mac_address(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Wi‑Fi MAC address",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def android_version_summary(self) -> Element:
        return self.android_version.get_sibling({"resource-id": "android:id/summary"})

    @property
    def ip_address(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "IP address",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def ip_address_summary(self) -> Element:
        return self.ip_address.get_sibling({"resource-id": "android:id/summary"})

    @property
    def wi_fi_mac_address_summary(self) -> Element:
        return self.wi_fi_mac_address.get_sibling({"resource-id": "android:id/summary"})

    @property
    def device_wi_fi_mac_address(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Device Wi‑Fi MAC address",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def device_wi_fi_mac_address_summary(self) -> Element:
        return self.device_wi_fi_mac_address.get_sibling({"resource-id": "android:id/summary"})

    @property
    def bluetooth_address(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Bluetooth address",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def bluetooth_address_summary(self) -> Element:
        return self.bluetooth_address.get_sibling({"resource-id": "android:id/summary"})

    @property
    def up_time(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Up time",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def up_time_summary(self) -> Element:
        return self.up_time.get_sibling({"resource-id": "android:id/summary"})

    @property
    def build_number(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Build number",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def build_number_summary(self) -> Element:
        return self.build_number.get_sibling({"resource-id": "android:id/summary"})

    @property
    def recycler(self) -> Element:
        return self.shadowstep.get_element(
            {
                "resource-id": "com.android.settings:id/content_parent",
                "class": "android.widget.ScrollView",
            }
        )

    @current_page()
    def is_current_page(self) -> bool:
        try:
            return self.title.is_visible()
        except Exception as error:
            self.logger.error(error)
            return False
