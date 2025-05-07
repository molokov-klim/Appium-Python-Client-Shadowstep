import logging

from shadowstep.element.element import Element
from shadowstep.page_base import PageBaseShadowstep


class PageExample(PageBaseShadowstep):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        return f"{self.name} ({self.__class__.__name__})"

    @property
    def edges(self):
        return {}

    @property
    def name(self) -> str:
        return "Example"

    @property
    def title(self) -> Element:
        return self.shadowstep.get_element({'text': 'Example',
                                            'class': 'android.widget.TextView'})

    def is_current_page(self) -> bool:
        try:
            return self.title.is_visible()
        except Exception as e:
            self.logger.error(e)
            return False
