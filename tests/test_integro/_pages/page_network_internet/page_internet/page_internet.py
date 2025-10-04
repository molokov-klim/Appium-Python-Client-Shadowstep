import logging
from typing import Any
from shadowstep.decorators.decorators import current_page
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageInternet(PageBaseShadowstep):

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Any]:
        return {"PageNetworkInternet": self.,
                "PageSavedNetworks": self.}

    @property
    def name(self) -> str:
        return "Internet"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element({
        'content-desc': 'Internet',
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
    def fix_connectivity(self) -> Element:
        return self.recycler.scroll_to_element({
            'content-desc': 'Fix connectivity',
            'class': 'android.widget.Button'
        })

    @property
    def pinned_header(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/pinned_header',
            'class': 'android.widget.FrameLayout'
        })

    @property
    def progress_bar_animation(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/progress_bar_animation',
            'class': 'android.widget.ProgressBar'
        })

    @property
    def add_network(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Add network',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def wi_fi(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Wi-Fi',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def wi_fi_switch(self) -> Element:
        return self.wi_fi.get_cousin(
            {
            'resource-id': 'android:id/switch_widget',
            'class': 'android.widget.Switch'
        })

    @property
    def t_mobile(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'T-Mobile',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def t_mobile_summary(self) -> Element:
        return self.t_mobile.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def androidwifi(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'AndroidWifi',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def androidwifi_summary(self) -> Element:
        return self.androidwifi.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def t_mobile_summary_1(self) -> Element:
        return self.t_mobile.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def network_preferences(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Network preferences',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def network_preferences_summary(self) -> Element:
        return self.network_preferences.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def saved_networks(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Saved networks',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def saved_networks_summary(self) -> Element:
        return self.saved_networks.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def non_carrier_data_usage(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Non-carrier data usage',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def non_carrier_data_usage_summary(self) -> Element:
        return self.non_carrier_data_usage.get_sibling({
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
            return self.title.is_visible()
        except Exception as error:
            self.logger.error(error)
            return False
