```
sdkmanager --update

sdkmanager "system-images;android-34;google_apis;x86_64" "platform-tools" "platforms;android-34" "emulator"
avdmanager create avd -n test_emulator -k "system-images;android-34;google_apis;x86_64" -d "Nexus 6"

emulator -avd test_emulator -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim
```
