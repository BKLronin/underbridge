# Underbridge for OP-Z
## Multitrack exporter
---

## Despription

- Exports Patterns and projects individual Audio Tracks to seperate folders for use in your DAW
- Python cross plattform with single file binary for x86 linux

![underbridge.jpg](:/5c0c93594d274c389d9290d79f1c542a)

## Installation 
### Ubuntu 20.10 LTS (If the binary in /dist doesn't work)

`sudo apt  install portaudio19-dev`
`sudo apt install python3-tk`
`pip install python-rtmidi`
`pip install pyaudio`

`python3 underbridge.py` to start

### Linux binary

``./underbridge``

Underbridge_alt was packaged on a different system. Might help if you run into problems.

## Steps

- connect OP-Z via USB
- in /dist/ directory run ``./underbridge``
- Alternatively python3 underbridge.py in root directory. Make sure you have installed dependencies before..

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





