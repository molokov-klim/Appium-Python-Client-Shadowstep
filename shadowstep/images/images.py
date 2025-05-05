from typing import Union, Iterator, Optional, List, Callable

from PIL.Image import Image
import numpy as np

from shadowstep.image.image import ShadowstepImage
from shadowstep.images.should import ImageShould


class ShadowstepImages:

    def __init__(
        self,
        image: Union[bytes, np.ndarray, Image, str],
        base: 'Shadowstep',
        threshold: float,
        timeout: float
    ):
        raise NotImplementedError

    def __iter__(self) -> Iterator[ShadowstepImage]:
        raise NotImplementedError

    def first(self) -> Optional[ShadowstepImage]:
        raise NotImplementedError

    def to_list(self) -> List[ShadowstepImage]:
        raise NotImplementedError

    def filter(
        self,
        predicate: Callable[[ShadowstepImage], bool]
    ) -> 'Images':
        raise NotImplementedError

    def refresh(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, idx: int) -> ShadowstepImage:
        raise NotImplementedError

    @property
    def should(self) -> ImageShould:
        raise NotImplementedError
