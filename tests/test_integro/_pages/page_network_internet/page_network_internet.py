# ruff: noqa
# pyright: ignore
import logging
from typing import Any
from shadowstep.decorators.common_decorators import current_page, log_info
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageNetworkInternet(PageBaseShadowstep):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Any]:
        return {"PageSettings": self.to_back, "PageInternet": self.to_internet}

    @property
    def name(self) -> str:
        return "Network & internet"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element(
            {
                "content-desc": "Network & internet",
                "resource-id": "com.android.settings:id/collapsing_toolbar",
                "class": "android.widget.FrameLayout",
            }
        )

    @log_info()
    def to_back(self):
        self.navigate_up.tap()
        return self.shadowstep.get_page("PageSettings")

    @log_info()
    def to_internet(self):
        self.internet.tap()
        return self.shadowstep.get_page("PageInternet")

    @property
    def navigate_up(self) -> Element:
        return self.recycler.scroll_to_element(
            {"content-desc": "Navigate up", "class": "android.widget.ImageButton"}
        )

    @property
    def vpn(self) -> Element:
        return self.recycler.scroll_to_element(
            {"text": "VPN", "resource-id": "android:id/title", "class": "android.widget.TextView"}
        )

    @property
    def airplane_mode(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Airplane mode",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def airplane_mode_switch(self) -> Element:
        return self.airplane_mode.get_cousin(
            {"resource-id": "android:id/switch_widget", "class": "android.widget.Switch"}
        )

    @property
    def internet(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Internet",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def internet_summary(self) -> Element:
        return self.internet.get_sibling({"resource-id": "android:id/summary"})

    @property
    def calls_sms(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Calls & SMS",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def calls_sms_summary(self) -> Element:
        return self.calls_sms.get_sibling({"resource-id": "android:id/summary"})

    @property
    def sims(self) -> Element:
        return self.recycler.scroll_to_element(
            {"text": "SIMs", "resource-id": "android:id/title", "class": "android.widget.TextView"}
        )

    @property
    def sims_summary(self) -> Element:
        return self.sims.get_sibling({"resource-id": "android:id/summary"})

    @property
    def hotspot_tethering(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Hotspot & tethering",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def hotspot_tethering_summary(self) -> Element:
        return self.hotspot_tethering.get_sibling({"resource-id": "android:id/summary"})

    @property
    def data_saver(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Data Saver",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def data_saver_summary(self) -> Element:
        return self.data_saver.get_sibling({"resource-id": "android:id/summary"})

    @property
    def mobile_plan(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Mobile plan",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def calls_sms_summary_1(self) -> Element:
        return self.calls_sms.get_sibling({"resource-id": "android:id/summary"})

    @property
    def vpn_summary(self) -> Element:
        return self.vpn.get_sibling({"resource-id": "android:id/summary"})

    @property
    def private_dns(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Private DNS",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def private_dns_summary(self) -> Element:
        return self.private_dns.get_sibling({"resource-id": "android:id/summary"})

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
