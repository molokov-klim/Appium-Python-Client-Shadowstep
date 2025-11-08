# ruff: noqa
# pyright: ignore
"""Tests for shadowstep.utils.translator module.

This module contains tests for the YandexTranslate class and its translation functionality.
"""

import os
from unittest.mock import Mock, patch

import pytest
import requests

from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepMissingYandexTokenError,
    ShadowstepTranslationFailedError,
)
from shadowstep.utils.translator import YandexTranslate


class TestYandexTranslate:
    """Test cases for YandexTranslate class."""

    @pytest.mark.unit
    def test_init_with_folder_id(self) -> None:
        """Test YandexTranslate initialization with folder ID."""
        with patch.object(YandexTranslate, "_get_iam_token", return_value="test_token"):
            translator = YandexTranslate("test_folder_id")
            assert translator.folder_id == "test_folder_id"  # noqa: S101
            assert translator._iam_token == "test_token"  # noqa: S101

    @patch.dict(os.environ, {"yandexPassportOauthToken": "test_oauth_token"})
    @patch("requests.Session")
    @pytest.mark.unit
    def test_get_iam_token_success(self, mock_session: Mock) -> None:
        """Test successful IAM token retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"iamToken": "test_iam_token"}
        mock_response.raise_for_status.return_value = None
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        translator = YandexTranslate("test_folder_id")
        assert translator._iam_token == "test_iam_token"  # noqa: S101
        session_mock.post.assert_called_once_with(
            "https://iam.api.cloud.yandex.net/iam/v1/tokens",
            json={"yandexPassportOauthToken": "test_oauth_token"},
            timeout=30,
            verify=False,
        )

    @patch.dict(os.environ, {}, clear=True)
    @pytest.mark.unit
    def test_get_iam_token_missing_oauth_token(self) -> None:
        """Test IAM token retrieval with missing OAuth token."""
        with pytest.raises(ShadowstepMissingYandexTokenError):
            YandexTranslate("test_folder_id")

    @patch.dict(os.environ, {"yandexPassportOauthToken": "test_oauth_token"})
    @patch("requests.Session")
    @pytest.mark.unit
    def test_get_iam_token_http_error(self, mock_session: Mock) -> None:
        """Test IAM token retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP Error")
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            YandexTranslate("test_folder_id")

    @pytest.mark.unit
    def test_contains_cyrillic_with_cyrillic(self) -> None:
        """Test _contains_cyrillic with text containing Cyrillic characters."""
        with patch.object(YandexTranslate, "_get_iam_token", return_value="test_token"):
            translator = YandexTranslate("test_folder_id")
            assert translator._contains_cyrillic("Привет мир") is True  # noqa: S101
            assert translator._contains_cyrillic("Hello Привет") is True  # noqa: S101
            assert translator._contains_cyrillic("тест") is True  # noqa: S101

    @pytest.mark.unit
    def test_contains_cyrillic_without_cyrillic(self) -> None:
        """Test _contains_cyrillic with text not containing Cyrillic characters."""
        with patch.object(YandexTranslate, "_get_iam_token", return_value="test_token"):
            translator = YandexTranslate("test_folder_id")
            assert translator._contains_cyrillic("Hello world") is False  # noqa: S101
            assert translator._contains_cyrillic("123456") is False  # noqa: S101
            assert translator._contains_cyrillic("") is False  # noqa: S101
            assert translator._contains_cyrillic("!@#$%^&*()") is False  # noqa: S101

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @pytest.mark.unit
    def test_translate_no_cyrillic(self, mock_get_token: Mock) -> None:
        """Test translate method with text not containing Cyrillic."""
        translator = YandexTranslate("test_folder_id")
        result = translator.translate("Hello world")
        assert result == "Hello world"  # noqa: S101

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @patch("requests.Session")
    @pytest.mark.unit
    def test_translate_success(self, mock_session: Mock, mock_get_token: Mock) -> None:
        """Test successful translation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "translations": [{"text": "Hello world"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"translations": [{"text": "Hello world"}]}'
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        translator = YandexTranslate("test_folder_id")
        result = translator.translate("Привет мир")

        assert result == "Hello world"  # noqa: S101
        session_mock.post.assert_called_once_with(
            "https://translate.api.cloud.yandex.net/translate/v2/translate",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
            },
            json={
                "folderId": "test_folder_id",
                "texts": ["Привет мир"],
                "sourceLanguageCode": "ru",
                "targetLanguageCode": "en",
            },
            timeout=30,
            verify=False,
        )

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @patch("requests.Session")
    @pytest.mark.unit
    def test_translate_http_error(self, mock_session: Mock, mock_get_token: Mock) -> None:
        """Test translation with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP Error")
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        translator = YandexTranslate("test_folder_id")

        with pytest.raises(requests.HTTPError):
            translator.translate("Привет мир")

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @patch("requests.Session")
    @pytest.mark.unit
    def test_translate_no_translations(self, mock_session: Mock, mock_get_token: Mock) -> None:
        """Test translation with empty translations response."""
        mock_response = Mock()
        mock_response.json.return_value = {"translations": []}
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"translations": []}'
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        translator = YandexTranslate("test_folder_id")

        with pytest.raises(ShadowstepTranslationFailedError):
            translator.translate("Привет мир")

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @patch("requests.Session")
    @pytest.mark.unit
    def test_translate_missing_translations_key(self, mock_session: Mock, mock_get_token: Mock) -> None:
        """Test translation with missing translations key in response."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{}'
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        translator = YandexTranslate("test_folder_id")

        with pytest.raises(ShadowstepTranslationFailedError):
            translator.translate("Привет мир")

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @patch("requests.Session")
    @pytest.mark.unit
    def test_translate_with_logging(self, mock_session: Mock, mock_get_token: Mock) -> None:
        """Test translation with logging calls."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "translations": [{"text": "Hello world"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"translations": [{"text": "Hello world"}]}'
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        translator = YandexTranslate("test_folder_id")
        translator.logger = Mock()

        result = translator.translate("Привет мир")

        assert result == "Hello world"  # noqa: S101
        # Check that debug logging was called
        assert translator.logger.debug.call_count >= 3  # noqa: S101

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @pytest.mark.unit
    def test_translate_empty_string(self, mock_get_token: Mock) -> None:
        """Test translation with empty string."""
        translator = YandexTranslate("test_folder_id")
        result = translator.translate("")
        assert result == ""  # noqa: S101

    @patch.object(YandexTranslate, "_get_iam_token", return_value="test_token")
    @patch("requests.Session")
    @pytest.mark.unit
    def test_translate_mixed_content(self, mock_session: Mock, mock_get_token: Mock) -> None:
        """Test translation with mixed Cyrillic and Latin content."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "translations": [{"text": "Hello Hello world"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"translations": [{"text": "Hello Hello world"}]}'
        session_mock = mock_session.return_value.__enter__.return_value
        session_mock.post.return_value = mock_response

        translator = YandexTranslate("test_folder_id")
        result = translator.translate("Hello Привет world")
        assert result == "Hello Hello world"  # noqa: S101
