# Underbridge for OP-Z
## Multitrack exporter
---

## Description

- Exports patterns and projects individual audio tracks to seperate folders for use in your DAW.
- Python cross plattform with single file binary for x86 linux Windows and Mac.

## Using Packaged single file Binarys _(The easy way)_

- Executables reside in the folder `/dist/` or in the release tab.
- on Windows
    ``underbridge.exe``
- On Linux:
    ``./underbridge``
- on Mac
Open termianl and change directpory to where the underbridge_mac file is and execute:
    ``chmod 755 underbridge_mac``
    ``./underbridge_mac`` or ``open underbridge_mac``

Underbridge_alt was packaged on a different system. Might help if you run into problems. (Outdated)

## Installation _(Less easy way)_

### Windows

- Install Python 3.9 if not already, 3.10 seems to cause problems.
- install mido :  `pip install mido`
- install rt-midi: `pip isntall rt-midi`
- install pipwin: `pip install pipwin`
- install pyaudio `pipwin install pyaudio`

**- Activate OP-Z device input in sound settings of windows and make it default (Should detect automatically just to be sure. **
**- Close all other Applications that might use any audio source like your Browser etc **

- run `python underbridge.py`

### Mac Install - ( tested on Mac OS Monterey 12.3 )

install portaudio: `brew install portaudio`
install mido: `pip install mido`
install tk: `brew install python-tk`
install rt-midi: `pip install python-rtmidi`
install pyaudio: `pip install pyaudio`

**Set OP-Z device as input in sound of system preferences**

open terminal and type: `python3 underbridge.py` to start

### Ubuntu 20.10 LTS

- `sudo apt  install portaudio19-dev`
- `sudo apt install python3-tk`
- `pip install python-rtmidi`
- `pip install pyaudio`

`python3 underbridge.py` to start

## Steps

- connect OP-Z via USB
- Run underbridge

### Single Pattern Mode

- Select Pattern you want to export
- Enter name for the project. This is used for the folder structure
- Get BPM from led code or Smartphone app.
- Enter BPM and longest Bar of you track (1-4)
- Optionally enter additional seconds at the end of the recording to capture reverb tails etc.
- Select pattern mode
- Select directory you want to record the waves to
- Click record and wait until finished.

### Project mode

- Select Porject and first Pattern you want to export on OP-Z.
- Enter name for the project. This is used for the folder structure
- Get BPM from led code or Smartphone app.
- Enter BPM
- Enter longest Bar of you track (1-4)
- Enter the Nr. of Patterns your song consists of.
- Optionally enter additional seconds at the end of the recording to capture reverb tails etc.
- Select project mode
- Select directory you want to record the waves to
- Click record and wait until finished.

### Troubleshooting
- When the recorded audio contains buzzing or other artifacts try disabling the USB charging with "display" and "bottom right key" to disable.
- If the playback of the OP-Z starts correctly but no tracks are muted check that MIDI IN in the OP-Z app or via combo is enabled.
