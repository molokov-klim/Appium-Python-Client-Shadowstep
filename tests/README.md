
# commands to install and run appium server
# use Google Pixel 14 android virtual device for testing

```commandline
uv lock --upgrade
uv sync
```

```commandline
sudo apt update
sudo apt install curl -y
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

sudo npm install -g appium@latest
sudo appium driver install uiautomator2

appium server -p 4723 -a 0.0.0.0 -pa /wd/hub --relaxed-security --log-level debug
```

android sdk (or install android studio)
```commandline
sudo apt update
sudo apt install android-sdk
export ANDROID_HOME=/usr/lib/android-sdk/   # adb version - check path to sdk root
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin
source ~/.bashrc
adb version
adb devices
```

# commands to start tests
```commandline
pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_shadowstep.py

pytest -svl --log-cli-level INFO --tb=short --setup-show tests/test_element.py
```
