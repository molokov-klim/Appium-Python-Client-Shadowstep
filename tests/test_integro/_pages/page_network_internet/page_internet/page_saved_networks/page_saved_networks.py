# SPDX-FileCopyrightText: 2023 Molokov Klim
#
# SPDX-License-Identifier: MIT

# ruff: noqa
# pyright: ignore
import logging
from typing import Any
from shadowstep.decorators.decorators import current_page, log_info
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageSavedNetworks(PageBaseShadowstep):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Any]:
        return {"PageInternet": self.to_back}

    @property
    def name(self) -> str:
        return "Saved networks"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element(
            {
                "content-desc": "Saved networks",
                "resource-id": "com.android.settings:id/collapsing_toolbar",
                "class": "android.widget.FrameLayout",
            }
        )

    @log_info()
    def to_back(self):
        self.navigate_up.tap()
        return self.shadowstep.get_page("PageInternet")

    @property
    def navigate_up(self) -> Element:
        return self.recycler.scroll_to_element(
            {"content-desc": "Navigate up", "class": "android.widget.ImageButton"}
        )

    @property
    def other_networks(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "Other networks",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def androidwifi(self) -> Element:
        return self.recycler.scroll_to_element(
            {
                "text": "AndroidWifi",
                "resource-id": "android:id/title",
                "class": "android.widget.TextView",
            }
        )

    @property
    def androidwifi_summary(self) -> Element:
        return self.androidwifi.get_sibling({"resource-id": "android:id/summary"})

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
