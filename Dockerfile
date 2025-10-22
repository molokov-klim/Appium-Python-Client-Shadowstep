FROM ubuntu:22.04

ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH=$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH
ENV PATH=$PATH:/usr/local/bin:/usr/bin
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including GStreamer (matching integration_tests.yml)
RUN apt-get update && apt-get install -y \
    wget unzip curl git openjdk-17-jdk \
    qemu-kvm libvirt-daemon-system libvirt-clients sudo \
    software-properties-common \
    gstreamer1.0-tools gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.9 (matching integration_tests.yml)
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.9 python3.9-distutils python3.9-dev && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9 && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js LTS (matching integration_tests.yml)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g appium@latest && \
    appium driver install uiautomator2

# Install uv and pytest
RUN python3.9 -m pip install uv pytest

RUN mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && cd $ANDROID_SDK_ROOT/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O cmdline-tools.zip && \
    unzip cmdline-tools.zip && mv cmdline-tools latest && rm cmdline-tools.zip

RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-34" "system-images;android-34;google_apis;x86_64" "emulator"

RUN echo "no" | avdmanager create avd -n test_avd -k "system-images;android-34;google_apis;x86_64" --force

RUN $ANDROID_SDK_ROOT/emulator/emulator -avd test_avd -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -snapshot save & \
    adb wait-for-device
