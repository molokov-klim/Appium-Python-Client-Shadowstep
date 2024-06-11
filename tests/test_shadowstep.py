class TestShadowstepBase:

    def test_connect(self, application):
        app = application
        assert app.driver is not None


class TestShadowstep:

    def test_get_element(self, application):
        app = application
        element = app.get_element(locator={'content-desc': 'Phone'})
        assert element.locator == {'content-desc': 'Phone'}


class TestElement:

    def test_tap(self, application):
        app = application
        element = app.get_element(locator={'content-desc': 'Phone'})
        element.tap()
