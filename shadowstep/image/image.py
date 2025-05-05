# shadowstep/image/image.py

import typing
from typing import Union, Tuple, Optional
import numpy as np
from PIL.Image import Image


class ShadowstepImage:
    """
    Lazy wrapper for image-based interactions
    """

    def __init__(
            self,
            image: Union[bytes, np.ndarray, Image, str],
            base: 'Shadowstep' = None,
            threshold: float = 0.9,
            timeout: float = 5.0
    ):
        self._image = image
        self._base = base
        self.threshold = threshold
        self.timeout = timeout
        self._coords: Optional[Tuple[int, int, int, int]] = None
        self._center: Optional[Tuple[int, int]] = None

    def tap(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def long_press(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def drag(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def wait(self) -> bool:
        raise NotImplementedError

    def wait_not(self) -> bool:
        raise NotImplementedError

    def get_image(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def get_images(self) -> typing.List['ShadowstepImage']:
        raise NotImplementedError

    def is_visible(self) -> bool:
        raise NotImplementedError

    def is_contains(self) -> bool:
        raise NotImplementedError

    def scroll_down(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def scroll_up(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def scroll_left(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def scroll_to(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def zoom(self) -> 'ShadowstepImage':
        raise NotImplementedError

    def unzoom(self) -> 'ShadowstepImage':
        raise NotImplementedError

    @property
    def coordinates(self) -> Tuple[int, int, int, int]:
        raise NotImplementedError

    @property
    def center(self) -> Tuple[int, int]:
        raise NotImplementedError

    @property
    def should(self) -> 'ImageShould':
        raise NotImplementedError
