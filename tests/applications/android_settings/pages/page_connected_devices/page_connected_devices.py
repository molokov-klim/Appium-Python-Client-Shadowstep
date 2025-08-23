import logging
from typing import Any

from shadowstep.decorators.decorators import current_page
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageConnectedDevices(PageBaseShadowstep):

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Any]:
        return {"PageSettings": self.to_main}

    def to_main(self):
        self.shadowstep.terminal.press_back()
        return self.shadowstep.get_page("PageSettings")

    @property
    def name(self) -> str:
        return "Connected devices"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element({
            'content-desc': 'Connected devices',
            'resource-id': 'com.android.settings:id/collapsing_toolbar',
            'class': 'android.widget.FrameLayout'
        })

    @property
    def navigate_up(self) -> Element:
        return self.recycler.scroll_to_element({
            'content-desc': 'Navigate up',
            'class': 'android.widget.ImageButton'
        })

    @property
    def pair_new_device(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Pair new device',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def saved_devices(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Saved devices',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def see_all(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'See all',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def visible_as_pixel_to_other(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Visible as “Pixel” to other devices',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def connection_preferences(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Connection preferences',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def connection_preferences_summary(self) -> Element:
        return self.connection_preferences.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def recycler(self) -> Element:
        return self.shadowstep.get_element({
            'resource-id': 'com.android.settings:id/content_parent',
            'class': 'android.widget.ScrollView'
        })

    @current_page()
    def is_current_page(self) -> bool:
        try:
            self.title.timeout = 3
            return self.title.is_visible()
        except Exception as error:
            self.logger.error(error)
            return False
