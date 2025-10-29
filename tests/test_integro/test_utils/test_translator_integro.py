# ruff: noqa
# pyright: ignore
"""Integration tests for translator.py YandexTranslate class."""

import os

import pytest

from shadowstep.exceptions.shadowstep_exceptions import ShadowstepMissingYandexTokenError
from shadowstep.shadowstep import Shadowstep
from shadowstep.utils.translator import YandexTranslate


class TestYandexTranslate:
    """Integration tests for YandexTranslate class."""

    def test_yandex_translate_class_exists(self, app: Shadowstep) -> None:
        """Test YandexTranslate class can be imported.

        Steps:
        1. Import YandexTranslate class.
        2. Verify class exists and has public methods.
        """
        # Verify class exists
        assert YandexTranslate is not None  # noqa: S101

        # Verify class has public methods
        assert hasattr(YandexTranslate, "__init__")  # noqa: S101
        assert hasattr(YandexTranslate, "translate")  # noqa: S101

    def test_yandex_translate_init_without_token(self, app: Shadowstep) -> None:
        """Test YandexTranslate initialization fails without token.

        Steps:
        1. Ensure yandexPassportOauthToken is not set.
        2. Try to create YandexTranslate instance.
        3. Verify ShadowstepMissingYandexTokenError is raised.
        """
        # Save current token if exists
        original_token = os.environ.get("yandexPassportOauthToken")

        try:
            # Remove token from environment
            if "yandexPassportOauthToken" in os.environ:
                del os.environ["yandexPassportOauthToken"]

            # Try to create instance without token
            with pytest.raises(ShadowstepMissingYandexTokenError):
                YandexTranslate(folder_id="test_folder")

        finally:
            # Restore original token if it existed
            if original_token is not None:
                os.environ["yandexPassportOauthToken"] = original_token

    def test_yandex_translate_behavior_with_english_text(self, app: Shadowstep) -> None:
        """Test that translate() behavior can be verified without calling it.

        Steps:
        1. Verify translate method signature exists.
        2. Verify method accepts text parameter.
        3. Verify return type is str.

        Note: Actual translation requires Yandex token, tested separately.
        """
        import inspect

        # Verify translate method exists
        assert hasattr(YandexTranslate, "translate")  # noqa: S101

        # Verify signature
        sig = inspect.signature(YandexTranslate.translate)
        assert "text" in sig.parameters  # noqa: S101
        assert sig.return_annotation == str  # noqa: S101

    def test_yandex_translate_class_structure(self, app: Shadowstep) -> None:
        """Test YandexTranslate class has correct structure.

        Steps:
        1. Verify class has expected attributes.
        2. Verify class has correct docstring.
        """
        # Verify class docstring
        assert YandexTranslate.__doc__ is not None  # noqa: S101
        assert "Yandex" in YandexTranslate.__doc__  # noqa: S101
        assert "translate" in YandexTranslate.__doc__.lower()  # noqa: S101

        # Verify __init__ signature
        import inspect

        sig = inspect.signature(YandexTranslate.__init__)
        assert "folder_id" in sig.parameters  # noqa: S101

        # Verify translate signature
        sig = inspect.signature(YandexTranslate.translate)
        assert "text" in sig.parameters  # noqa: S101

    def test_yandex_translate_method_signatures(self, app: Shadowstep) -> None:
        """Test YandexTranslate methods have correct signatures.

        Steps:
        1. Verify all public methods have correct parameters.
        2. Verify return type annotations are present.
        """
        import inspect

        # Verify translate method signature
        sig = inspect.signature(YandexTranslate.translate)
        assert "text" in sig.parameters  # noqa: S101
        assert sig.return_annotation == str  # noqa: S101

        # Verify __init__ signature
        sig = inspect.signature(YandexTranslate.__init__)
        assert "folder_id" in sig.parameters  # noqa: S101
        assert sig.parameters["folder_id"].annotation == str  # noqa: S101
