from setuptools import setup

setup(
    name="underbridge",
    version="1.0.0",
    description="Underbridge OP-Z multichannel exporter",
    author="Thomas Herrmann",
    author_email="herrmann@raise-uav.com",
    py_modules=["underbridge"],
    install_requires=[
        "mido",
        "pyaudio",
        "nicegui",
    ],
    entry_points={
        "console_scripts": [
            "underbridge=underbridge:main",
        ],
    },
)