import inspect
import logging
import os
from typing import Optional, Tuple, List, Dict, Any

from shadowstep.page_object.page_object_parser import PageObjectParser
from shadowstep.page_object.page_object_generator import PageObjectGenerator
from shadowstep.page_object.page_object_recycler_explorer import PageObjectRecyclerExplorer
from shadowstep.shadowstep import Shadowstep


class PageObjectBuilder:
    """Orchestrates the full PageObject generation: from static XML to dynamically discovered elements."""

    def __init__(self, shadowstep: Shadowstep):
        self.logger = logging.getLogger(__name__)
        self.shadowstep = shadowstep

        self.parser = PageObjectParser()
        self.generator = PageObjectGenerator(self.parser)
        self.explorer = PageObjectRecyclerExplorer(self.shadowstep)

        self.initial_path: Optional[str] = None
        self.generated_class_name: Optional[str] = None
        self.additional_elements: List[Dict[str, Any]] = []

    def generate_initial(self, source_xml: str, output_dir: str) -> Tuple[str, str]:
        """Generates the base PageObject using static XML."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        path, class_name = self.generator.generate(
            source_xml=source_xml,
            output_dir=output_dir,
        )
        self.initial_path = path
        self.generated_class_name = class_name
        return path, class_name

    def discover_recycler(self) -> None:
        """Finds additional elements inside recycler if present."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if not self.initial_path or not self.generated_class_name:
            raise RuntimeError("generate_initial() must be called before discover_recycler().")

        result = self.explorer.explore(
            input_path=self.initial_path,
            class_name=self.generated_class_name,
            output_dir=self.initial_path  # временно пишем в тот же путь
        )
        if result:
            _, _ = result
        else:
            self.logger.warning("No additional elements discovered.")

    def combine_all(self, output_dir: Optional[str] = None) -> Tuple[str, str]:
        """Re-generates PageObject with discovered elements combined."""
        self.logger.debug(f"{inspect.currentframe().f_code.co_name}")

        if not self.initial_path or not self.generated_class_name:
            raise RuntimeError("Must call generate_initial() before combine_all().")

        xml = self.shadowstep.driver.page_source
        final_output_dir = output_dir or os.path.dirname(self.initial_path)

        return self.generator.generate(
            source_xml=xml,
            output_dir=final_output_dir,
        )
