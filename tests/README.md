
# commands to install and run appium server
# use Google Pixel virtual device for testing

```commandline
pip install -r requirements-dev.txt
```

```commandline
npm install -g appium@latest
appium driver install uiautomator2
appium server -p 4723 -a 0.0.0.0 -pa /wd/hub --relaxed-security --log-level debug
```


# probably must install android studio

# commands to start tests

```commandline
pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_shadowstep.py

pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_element.py
```



