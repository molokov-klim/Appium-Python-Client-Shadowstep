FROM ubuntu:22.04

ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH=$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH
ENV PATH=$PATH:/usr/local/bin:/usr/bin

RUN apt-get update && apt-get install -y \
    wget unzip curl git python3 python3-pip openjdk-17-jdk \
    qemu-kvm libvirt-daemon-system libvirt-clients sudo && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g appium@latest && \
    appium driver install uiautomator2

RUN pip3 install uv pytest

RUN mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && cd $ANDROID_SDK_ROOT/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O cmdline-tools.zip && \
    unzip cmdline-tools.zip && mv cmdline-tools latest && rm cmdline-tools.zip

RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-34" "system-images;android-34;google_apis;x86_64" "emulator"

RUN echo "no" | avdmanager create avd -n test_avd -k "system-images;android-34;google_apis;x86_64" --force

RUN $ANDROID_SDK_ROOT/emulator/emulator -avd test_avd -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -snapshot save & \
    adb wait-for-device
