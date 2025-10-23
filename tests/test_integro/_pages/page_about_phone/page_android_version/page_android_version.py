# ruff: noqa
# pyright: ignore
import logging
from typing import Any
from shadowstep.decorators.decorators import current_page, log_info
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageAndroidVersion(PageBaseShadowstep):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Any]:
        return {"PageAboutPhone": self.to_back}

    @property
    def name(self) -> str:
        return "Android version"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element(
            {
                "content-desc": "Android version",
                "resource-id": "com.android.settings:id/collapsing_toolbar",
                "class": "android.widget.FrameLayout",
            }
        )

    @log_info()
    def to_back(self):
        self.navigate_up.tap()
        return self.shadowstep.get_page("PageAboutPhone")

    @property
    def navigate_up(self) -> Element:
        return self.recycler.scroll_to_element(
            {"content-desc": "Navigate up", "class": "android.widget.ImageButton"}
        )

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
    def android_version_summary(self) -> Element:
        return self.android_version.get_sibling({"resource-id": "android:id/summary"})

    @property
    def android_security_update(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Android security update",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def android_security_update_summary(self) -> Element:
        return self.android_security_update.get_sibling({"resource-id": "android:id/summary"})

    @property
    def google_play_system_update(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Google Play system update",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def google_play_system_update_summary(self) -> Element:
        return self.google_play_system_update.get_sibling({"resource-id": "android:id/summary"})

    @property
    def baseband_version(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Baseband version",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def baseband_version_summary(self) -> Element:
        return self.baseband_version.get_sibling({"resource-id": "android:id/summary"})

    @property
    def kernel_version(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Kernel version",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def kernel_version_summary(self) -> Element:
        return self.kernel_version.get_sibling({"resource-id": "android:id/summary"})

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
