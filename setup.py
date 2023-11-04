import subprocess

from setuptools import setup, find_packages

# Общее описание пакета
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


VERSION = '0.0.1'


setup(
    name='shadowstep',
    version=VERSION,
    description='UI Testing Framework powered by Appium Python Client',
    long_description=long_description,
    author='molokov-klim',
    packages=find_packages(),
    install_requires=[
        'Appium-Python-Client==2.11.1',
        'allure-pytest==2.13.2',
        "zlib-compress==0.0.1",
        "zlib-decompress==0.0.2",
        "pylibjpeg==1.4.0",
        'Pillow==9.5.0',
        'requests==2.31.0',
        'pyserial==3.5',
        'opencv-python==4.8.0.74',
        'pytesseract==0.3.10',
        'numpy==1.25.1',
        'selenium==4.10.0',
    ],
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    url='https://github.com/molokov-klim/shadowstep',
)
