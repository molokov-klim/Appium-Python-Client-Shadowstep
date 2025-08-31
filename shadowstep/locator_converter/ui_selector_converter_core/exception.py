
class LocatorConverterError(Exception):
    """Base exception for locator conversion errors."""
    pass


class InvalidUiSelectorError(LocatorConverterError):
    """Raised when UiSelector string is malformed."""
    pass


class ConversionError(LocatorConverterError):
    """Raised when conversion between formats fails."""
    pass
