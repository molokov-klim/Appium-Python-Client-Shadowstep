import logging
from typing import Any

from shadowstep.decorators.decorators import current_page
from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep
from shadowstep.utils.utils import get_current_func_name


class PageSettings(PageBaseShadowstep):

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self) -> dict[str, Any]:
        return {"PageNetworkInternet": self.to_network_internet,
                "PageConnectedDevices": self.to_connected_devices}

    def to_connected_devices(self):
        self.logger.info(get_current_func_name())
        self.connected_devices.tap()
        return self.shadowstep.get_page("PageConnectedDevices")

    def to_network_internet(self):
        self.logger.info(get_current_func_name())
        self.logger.info(self.network_internet.get_attributes())
        self.network_internet.tap()
        return self.shadowstep.get_page("PageNetworkInternet")

    @property
    def name(self) -> str:
        return "Settings"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element({
        'text': 'Settings',
        'resource-id': 'com.android.settings:id/homepage_title',
        'class': 'android.widget.TextView'
    })

    @property
    def app_bar_container(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/app_bar_container',
            'class': 'android.widget.LinearLayout'
        })

    @property
    def homepage_app_bar_regular_phone_view(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/homepage_app_bar_regular_phone_view',
            'class': 'android.widget.LinearLayout'
        })

    @property
    def search_bar(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/search_bar',
            'class': 'androidx.cardview.widget.CardView'
        })

    @property
    def search_action_bar(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/search_action_bar',
            'class': 'android.view.ViewGroup'
        })

    @property
    def search_settings(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Search settings',
            'resource-id': 'com.android.settings:id/search_action_bar_title',
            'class': 'android.widget.TextView'
        })

    @property
    def main_content_scrollable_container(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/main_content_scrollable_container',
            'class': 'android.widget.ScrollView'
        })

    @property
    def homepage_container(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/homepage_container',
            'class': 'android.widget.LinearLayout'
        })

    @property
    def text_frame(self) -> Element:
        return self.recycler.scroll_to_element({
            'resource-id': 'com.android.settings:id/text_frame',
            'class': 'android.widget.RelativeLayout'
        })

    @property
    def network_internet(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Network & internet',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def network_internet_summary(self) -> Element:
        return self.network_internet.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def connected_devices(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Connected devices',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def connected_devices_summary(self) -> Element:
        return self.connected_devices.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def apps(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Apps',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def apps_summary(self) -> Element:
        return self.apps.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def notifications(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Notifications',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def notifications_summary(self) -> Element:
        return self.notifications.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def battery(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Battery',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def battery_summary(self) -> Element:
        return self.battery.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def settings_homepage_container(self) -> Element:
        return self.shadowstep.get_element({
            'resource-id': 'com.android.settings:id/settings_homepage_container',
            'class': 'android.widget.ScrollView'
        })

    @property
    def security(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Security',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def security_summary(self) -> Element:
        return self.security.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def privacy(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Privacy',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def privacy_summary(self) -> Element:
        return self.privacy.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def location(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Location',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def location_summary(self) -> Element:
        return self.location.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def safety_emergency(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Safety & emergency',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def safety_emergency_summary(self) -> Element:
        return self.safety_emergency.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def passwords_accounts(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'Passwords & accounts',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def passwords_accounts_summary(self) -> Element:
        return self.passwords_accounts.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def system(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'System',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def system_summary(self) -> Element:
        return self.system.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def about_phone(self) -> Element:
        return self.recycler.scroll_to_element({
            'text': 'About phone',
            'resource-id': 'android:id/title',
            'class': 'android.widget.TextView'
        })

    @property
    def about_phone_summary(self) -> Element:
        return self.about_phone.get_sibling({
            'resource-id': 'android:id/summary'
        })

    @property
    def recycler(self) -> Element:
        return self.shadowstep.get_element({
            'resource-id': 'com.android.settings:id/settings_homepage_container',
            'class': 'android.widget.ScrollView'
        })

    @current_page()
    def is_current_page(self) -> bool:
        try:
            return self.title.is_visible()
        except Exception as error:
            self.logger.error(error)
            return False
