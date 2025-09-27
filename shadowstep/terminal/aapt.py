"""AAPT (Android Asset Packaging Tool) integration for Shadowstep framework.

This module provides the Aapt class for extracting package information
from APK files using the Android Asset Packaging Tool, including
package names and launchable activities.
"""
# shadowstep/terminal/aapt.py

import logging
import os
import subprocess

from shadowstep.utils.utils import get_current_func_name

logger = logging.getLogger(__name__)


class Aapt:
    """Android Asset Packaging Tool (AAPT) integration.

    This class provides functionality to extract package information
    from APK files using the Android Asset Packaging Tool, including
    package names and launchable activities.
    """

    @staticmethod
    def get_package_name(path_to_apk: str) -> str:
        """Get APK file package name using aapt command.

        Returns package name.
        """
        logger.info(f"{get_current_func_name()} < {path_to_apk}")

        command = ["aapt", "dump", "badging", os.path.join(path_to_apk)]

        try:
            # Execute command and get output
            output: str = str(subprocess.check_output(command)).strip()  # noqa: S603

            # Extract string containing package information
            start_index = output.index("package: name='") + len("package: name='")
            end_index = output.index("'", start_index)

            # Extract package name
            package_name = output[start_index:end_index]

        except subprocess.CalledProcessError as e:
            logger.error(f"Could not extract package name. Error: {str(e)}")
            raise  # Re-raise exception

        except ValueError:
            logger.error("Could not find package name in the output.")
            raise  # Re-raise exception

        logger.info(f"{get_current_func_name()} > {package_name}")
        # Return package name as string
        return package_name

    @staticmethod
    def get_launchable_activity(path_to_apk: str) -> str:
        """Get launchable activity name from APK file using aapt command.

        Returns activity name as string.
        """
        logger.info(f"{get_current_func_name()} < {path_to_apk}")

        command = ["aapt", "dump", "badging", path_to_apk]

        try:
            # Execute command and get output
            output = subprocess.check_output(command, universal_newlines=True).strip()  # noqa: S603

            # Extract string containing launchable activity information
            package_line = next(line for line in output.splitlines() if line.startswith("launchable-activity"))

            # Extract activity name from string
            launchable_activity = package_line.split("'")[1]

            # Return activity name as string
            logger.info(f"{get_current_func_name()} > {launchable_activity}")
            return launchable_activity
        except subprocess.CalledProcessError as e:
            logger.error(f"Could not extract launchable activity. Error: {str(e)}")
        except StopIteration:
            logger.error("Could not find 'launchable-activity' line in aapt output.")

        return ""
