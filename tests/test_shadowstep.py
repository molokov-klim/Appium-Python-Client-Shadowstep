
def test_connect(application):
    app = application
    assert app.driver is not None


def test_get_element(application):
    app = application
    element = app.get_element(locator={'resource-id': 'ru.sigma.app.debug:id/buttonThree'})
    assert element.locator == {'resource-id': 'ru.sigma.app.debug:id/buttonThree'}


def test_tap(application):
    app = application
    element = app.get_element(locator={'resource-id': 'ru.sigma.app.debug:id/buttonThree'})
    element.tap()
