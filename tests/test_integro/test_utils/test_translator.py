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

    @pytest.mark.skipif(
        not os.getenv("yandexPassportOauthToken"),
        reason="Yandex token not available"
    )
    def test_yandex_translate_init_with_token(self, app: Shadowstep) -> None:
        """Test YandexTranslate initialization with valid token.

        Steps:
        1. Create YandexTranslate instance with token from environment.
        2. Verify instance is created successfully.
        3. Verify public attributes are accessible.

        Note: This test only runs if yandexPassportOauthToken is set.
        """
        # Create instance with folder_id
        translator = YandexTranslate(folder_id="test_folder")

        # Verify instance exists
        assert translator is not None  # noqa: S101

        # Verify public attribute
        assert translator.folder_id == "test_folder"  # noqa: S101

    @pytest.mark.skipif(
        not os.getenv("yandexPassportOauthToken") or not os.getenv("YANDEX_FOLDER_ID"),
        reason="Yandex credentials not available"
    )
    def test_yandex_translate_translate_english(self, app: Shadowstep) -> None:
        """Test translate() returns original for English text.

        Steps:
        1. Create YandexTranslate instance.
        2. Call translate() with English text.
        3. Verify original text is returned (no translation needed).

        Note: This test only runs if yandexPassportOauthToken is set.
        """
        # Create translator with real folder_id from environment
        folder_id = os.getenv("YANDEX_FOLDER_ID", "test_folder")
        translator = YandexTranslate(folder_id=folder_id)

        # Translate English text (should return original)
        english_text = "Hello world"
        result = translator.translate(english_text)

        # Should return original text since no Cyrillic
        assert result == english_text  # noqa: S101

    @pytest.mark.skipif(
        not os.getenv("yandexPassportOauthToken") or not os.getenv("YANDEX_FOLDER_ID"),
        reason="Yandex credentials not available"
    )
    def test_yandex_translate_translate_russian(self, app: Shadowstep) -> None:
        """Test translate() translates Russian text to English.

        Steps:
        1. Create YandexTranslate instance.
        2. Call translate() with Russian text.
        3. Verify translated English text is returned.

        Note: This test only runs if credentials are set.
        """
        # Create translator with real folder_id from environment
        folder_id = os.getenv("YANDEX_FOLDER_ID", "test_folder")
        translator = YandexTranslate(folder_id=folder_id)

        # Translate Russian text
        russian_text = "Привет"
        result = translator.translate(russian_text)

        # Should return translated text
        assert result != russian_text  # noqa: S101
        assert isinstance(result, str)  # noqa: S101
        assert len(result) > 0  # noqa: S101

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
