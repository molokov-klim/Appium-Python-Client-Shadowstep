from typing import Union, Tuple, Dict


class Element:
    def __init__(self,
                 locator: Union[Tuple, Dict[str, str], str] = None,
                 contains: bool = True
                 ):
        self.locator = locator
        self.contains = contains



