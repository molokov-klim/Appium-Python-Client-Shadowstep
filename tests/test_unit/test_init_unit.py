# ruff: noqa
# pyright: ignore
"""Tests for shadowstep package initialization and logging configuration."""

import logging
import pytest
from unittest.mock import Mock, patch
from shadowstep import LoguruStyleFormatter, configure_logging


class TestLoguruStyleFormatter:
    """Test cases for LoguruStyleFormatter class."""

    @pytest.mark.unit
    def test_formatter_initialization(self):
        """Test LoguruStyleFormatter initialization."""
        formatter = LoguruStyleFormatter()
        assert formatter is not None
        assert hasattr(formatter, 'COLORS')
        assert hasattr(formatter, 'RESET')

    @pytest.mark.unit
    def test_colors_defined(self):
        """Test that all log level colors are defined."""
        formatter = LoguruStyleFormatter()
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in expected_levels:
            assert level in formatter.COLORS
            assert isinstance(formatter.COLORS[level], str)
            assert formatter.COLORS[level].startswith("\033[")

    @pytest.mark.unit
    def test_reset_code_defined(self):
        """Test that reset code is defined."""
        formatter = LoguruStyleFormatter()
        assert formatter.RESET == "\033[0m"

    @pytest.mark.unit
    def test_format_debug_record(self):
        """Test formatting a DEBUG level log record."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Debug message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "DEBUG" in result
        assert "test.logger" in result
        assert "Debug message" in result
        assert "\033[38;5;81m" in result  # Light blue for DEBUG

    @pytest.mark.unit
    def test_format_info_record(self):
        """Test formatting an INFO level log record."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Info message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "INFO" in result
        assert "test.logger" in result
        assert "Info message" in result
        assert "\033[38;5;34m" in result  # Green for INFO

    @pytest.mark.unit
    def test_format_warning_record(self):
        """Test formatting a WARNING level log record."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "WARNING" in result
        assert "test.logger" in result
        assert "Warning message" in result
        assert "\033[38;5;220m" in result  # Yellow for WARNING

    @pytest.mark.unit
    def test_format_error_record(self):
        """Test formatting an ERROR level log record."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "ERROR" in result
        assert "test.logger" in result
        assert "Error message" in result
        assert "\033[38;5;196m" in result  # Red for ERROR

    @pytest.mark.unit
    def test_format_critical_record(self):
        """Test formatting a CRITICAL level log record."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.CRITICAL,
            pathname="test.py",
            lineno=1,
            msg="Critical message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "CRITICAL" in result
        assert "test.logger" in result
        assert "Critical message" in result
        assert "\033[1;41m" in result  # White on red for CRITICAL

    @pytest.mark.unit
    def test_format_unknown_level(self):
        """Test formatting a log record with unknown level."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="test.logger",
            level=25,  # Custom level between INFO and WARNING
            pathname="test.py",
            lineno=1,
            msg="Custom level message",
            args=(),
            exc_info=None
        )
        record.levelname = "CUSTOM"
        
        result = formatter.format(record)
        
        # Should not have color for unknown level
        assert "CUSTOM" in result
        assert "test.logger" in result
        assert "Custom level message" in result

    @pytest.mark.unit
    def test_format_includes_timestamp(self):
        """Test that formatted output includes timestamp."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        # Should contain gray color code for timestamp
        assert "\033[38;5;240m" in result
        # Should contain pipe separators
        assert "|" in result

    @pytest.mark.unit
    def test_format_includes_logger_name_with_color(self):
        """Test that formatted output includes colored logger name."""
        formatter = LoguruStyleFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        
        record = logging.LogRecord(
            name="shadowstep.test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        # Should contain purple color code for logger name
        assert "\033[38;5;135m" in result
        assert "shadowstep.test" in result


class TestConfigureLogging:
    """Test cases for configure_logging function."""

    @pytest.mark.unit
    def test_configure_logging_creates_logger(self):
        """Test that configure_logging creates shadowstep logger."""
        # Get the logger after configuration
        logger = logging.getLogger("shadowstep")
        
        assert logger is not None
        assert logger.level == logging.INFO

    @pytest.mark.unit
    def test_configure_logging_adds_handler(self):
        """Test that configure_logging adds handler to logger."""
        logger = logging.getLogger("shadowstep")
        
        assert len(logger.handlers) > 0
        # Check that at least one handler has LoguruStyleFormatter
        has_custom_formatter = any(
            isinstance(handler.formatter, LoguruStyleFormatter)
            for handler in logger.handlers
        )
        assert has_custom_formatter

    @pytest.mark.unit
    def test_configure_logging_sets_formatter(self):
        """Test that configure_logging sets custom formatter."""
        logger = logging.getLogger("shadowstep")
        
        # Check first handler has LoguruStyleFormatter
        if logger.handlers:
            formatter = logger.handlers[0].formatter
            assert isinstance(formatter, LoguruStyleFormatter)

    @pytest.mark.unit
    def test_configure_logging_propagate_false(self):
        """Test that configure_logging sets propagate to False."""
        logger = logging.getLogger("shadowstep")
        
        assert logger.propagate is False

    @pytest.mark.unit
    @patch('logging.getLogger')
    def test_configure_logging_idempotent(self, mock_get_logger):
        """Test that configure_logging can be called multiple times safely."""
        # Create mock logger with existing handlers
        mock_logger = Mock(spec=logging.Logger)
        mock_logger.handlers = [Mock(spec=logging.StreamHandler)]
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        # Call configure_logging
        configure_logging()
        
        # Verify logger was retrieved
        mock_get_logger.assert_called()
        # Handler should not be added again since handlers already exist
        mock_logger.addHandler.assert_not_called()

    @pytest.mark.unit
    def test_logger_can_log_messages(self):
        """Test that configured logger can log messages."""
        logger = logging.getLogger("shadowstep.test")
        
        # This should not raise any exceptions
        logger.debug("Debug test message")
        logger.info("Info test message")
        logger.warning("Warning test message")
        logger.error("Error test message")
        logger.critical("Critical test message")

    @pytest.mark.unit
    def test_configure_logging_applies_to_root_logger(self):
        """Test that configure_logging applies configuration to root logger."""
        shadowstep_logger = logging.getLogger("shadowstep")
        root_logger = logging.getLogger()
        
        # Root logger should have same handlers as shadowstep logger
        assert root_logger.handlers == shadowstep_logger.handlers
        assert root_logger.level == shadowstep_logger.level

