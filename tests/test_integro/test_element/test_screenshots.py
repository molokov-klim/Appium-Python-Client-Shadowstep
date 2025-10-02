from typing import Any

from shadowstep.shadowstep import Shadowstep


class TestScreenshots:
    def test_screenshot_as_base64(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        ss = el.screenshot_as_base64
        assert isinstance(ss, str)  # noqa: S101  # noqa: S101

    def test_screenshot_as_png(self, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        ss = el.screenshot_as_png
        assert isinstance(ss, bytes)  # noqa: S101  # noqa: S101

    def test_save_screenshot(self, tmp_path: Any, app: Shadowstep, press_home: Any, stability: None):
        el = app.get_element({"content-desc": "Phone"})
        filepath = tmp_path / "test_element.png"
        assert el.save_screenshot(str(filepath)) is True  # noqa: S101  # noqa: S101
        assert filepath.exists()  # noqa: S101  # noqa: S101
        filepath.unlink()
        assert not filepath.exists()  # noqa: S101  # noqa: S101
