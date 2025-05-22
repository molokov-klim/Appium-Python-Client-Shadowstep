
# commands to install and run appium server
# use Google Pixel virtual device for testing

```commandline
pip install -r requirements-dev.txt
```

```commandline
npm i -g appium@next
appium driver install uiautomator2
appium server -ka 800 --log-level debug -p 4723 -a 0.0.0.0 -pa /wd/hub --allow-insecure=adb_shell
```


# probably must install android studio

# commands to start tests

```commandline
pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_shadowstep.py
```
