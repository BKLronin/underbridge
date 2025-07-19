import sys
import os
import time
import threading
import wave

import mido
import pyaudio

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QRadioButton, QSpinBox,
    QCheckBox, QFileDialog
)
from PySide6.QtCore import Qt


class Midirecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("underbridge")
        self.setFixedSize(700, 400)

        # Styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #666;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #333;
            }

            QRadioButton {
                background-color: #2f2f2f;
                color: white;
                border: 1px solid #666;
                border-radius: 8px;
                padding: 4px 10px;
            }
            QRadioButton::indicator { width: 0px; height: 0px; }
            QRadioButton:checked {
                background-color: #0095FF;
                color: black;
            }

            QCheckBox { color: white; }
            QLineEdit {
                background-color: #999;
                color: black;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 2px 6px;
            }
            QLabel { color: white; }
            QGroupBox {
                border: 1px solid #666;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: white;
            }
            QSpinBox {
                background-color: #999;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 2px;
                color: black;
            }
            QLabel#footer {
                color: #aaa;
                font-size: 10px;
            }
            QLabel#display {
                background: #aaa;
                color: black;
                padding: 4px;
                border-radius: 4px;
            }
        """)

        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Parameter group
        param_group = QGroupBox("Parameter")
        param_layout = QGridLayout(param_group)
        self.name_input = QLineEdit("Name")
        self.bpm_input = QLineEdit("BPM")
        self.bar_input = QSpinBox()
        self.bar_input.setRange(1, 9)
        self.patterns_input = QSpinBox()
        self.patterns_input.setRange(1, 16)
        self.patterns_input.setValue(16)
        self.add_sec = QSpinBox()
        self.add_sec.setRange(0, 10)

        param_layout.addWidget(self.name_input, 0, 0)
        param_layout.addWidget(self.bpm_input, 0, 1)
        param_layout.addWidget(QLabel("Nr. Bars"), 0, 2)
        param_layout.addWidget(self.bar_input, 0, 3)
        param_layout.addWidget(QLabel("Patterns"), 0, 4)
        param_layout.addWidget(self.patterns_input, 0, 5)
        param_layout.addWidget(QLabel("Extra Sec"), 0, 6)
        param_layout.addWidget(self.add_sec, 0, 7)

        # Mode selection
        self.mode_select_project = QRadioButton("Project")
        self.mode_select_pattern = QRadioButton("Pattern")
        self.mode_select_pattern.setChecked(True)

        # Modifiers group
        modifier_group = QGroupBox("Exclude Modifiers")
        modifier_layout = QGridLayout(modifier_group)
        self.modifiers = []
        for i, name in enumerate(["Send 1", "Send 2", "Tape", "Master", "Perform", "Module"]):
            cb = QCheckBox(name)
            modifier_layout.addWidget(cb, 0, i)
            self.modifiers.append(cb)

        # Control buttons and display
        controls_layout = QGridLayout()
        self.set_param_button = QPushButton("Set Prmtr")
        self.set_path_button = QPushButton("Directory")
        self.record_button = QPushButton("RECORD")
        self.cancel_button = QPushButton("CANCEL")
        self.display_label = QLabel("Enter Parameter, then press Set Param...")
        self.display_label.setObjectName("display")

        self.set_param_button.clicked.connect(self.setParam)
        self.set_path_button.clicked.connect(self.setPath)
        self.cancel_button.clicked.connect(self.cancelRec)
        self.record_button.clicked.connect(lambda: threading.Thread(target=self.sequenceMaster).start())

        controls_layout.addWidget(self.mode_select_project, 0, 0)
        controls_layout.addWidget(self.mode_select_pattern, 0, 1)
        controls_layout.addWidget(self.set_param_button, 0, 2)
        controls_layout.addWidget(self.set_path_button, 0, 3)
        controls_layout.addWidget(self.record_button, 0, 4)
        controls_layout.addWidget(self.cancel_button, 0, 5)
        controls_layout.addWidget(self.display_label, 1, 0, 1, 6)

        # Footer
        footer_label = QLabel("donate <3 @ https://link.raise-uav.com")
        footer_label.setObjectName("footer")

        # Layout
        main_layout.addWidget(param_group)
        main_layout.addWidget(modifier_group)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(footer_label)
        self.setCentralWidget(main_widget)

        # Internal state
        self.op_device = []
        self.audio_device = []
        self.loop_time = 0
        self.outport = None
        self.pattern_nr = 0
        self.j = 0
        self.projectpath = ""
        self.cancel = 0
        self.RATE = 0
        self.mute_list = [0] * 14

    def getMIDIDevice(self):
        try:
            device_list = mido.get_output_names()
            self.op_device = [d for d in device_list if 'OP-Z' in d][0]
            self.display_label.setText("OP-Z found")
        except Exception as e:
            self.display_label.setText(f"MIDI Error: {e}")

    def getAudioDevice(self):
        try:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            for i in range(info['deviceCount']):
                dev = p.get_device_info_by_host_api_device_index(0, i)
                if 'OP-Z' in dev['name'] and dev['maxInputChannels'] > 0:
                    self.audio_device = i
                    break
            devinfo = p.get_device_info_by_index(self.audio_device)
            p.is_format_supported(48000, input_device=devinfo['index'], input_channels=devinfo['maxInputChannels'], input_format=pyaudio.paInt16)
            self.RATE = 48000
        except Exception as e:
            self.RATE = 44100
            self.display_label.setText(f"Audio Error: {e}")

    def openMidi(self):
        try:
            self.outport = mido.open_output(self.op_device)
        except Exception as e:
            self.display_label.setText(f"Open MIDI Error: {e}")

    def closeMidi(self):
        try:
            if self.outport:
                self.outport.close()
                self.display_label.setText("MIDI closed")
        except Exception as e:
            self.display_label.setText(f"Close MIDI Error: {e}")

    def start_Rec(self):
        try:
            self.display_label.setText("Recording...")
            CHUNK = 128
            FORMAT = pyaudio.paInt16
            CHANNELS = 2
            RECORD_SECONDS = self.loop_time
            WAVE_OUTPUT_FILENAME = f"{self.name_input.text()}_track{self.j+1}.wav"
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=self.RATE,
                            input=True,
                            input_device_index=self.audio_device,
                            frames_per_buffer=CHUNK)

            frames = []
            self.start_MIDI()
            for _ in range(0, int(self.RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            folder = self.projectpath
            if self.mode_select_project.isChecked():
                folder = os.path.join(folder, str(self.pattern_nr))

            os.makedirs(folder, exist_ok=True)
            wf = wave.open(os.path.join(folder, WAVE_OUTPUT_FILENAME), 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            self.j = (self.j + 1) % 8
            self.display_label.setText("End of Recording")
        except Exception as e:
            self.display_label.setText(f"Recording Error: {e}")

    def start_MIDI(self):
        try:
            self.openMidi()
            self.muteAll()
        except Exception as e:
            self.display_label.setText(f"Start MIDI Error: {e}")

    def stop_MIDI(self):
        try:
            self.muteAll()
            self.closeMidi()
        except Exception as e:
            self.display_label.setText(f"Stop MIDI Error: {e}")

    def muteAll(self):
        try:
            if not self.outport:
                self.display_label.setText("MIDI port not open for muteAll")
                return
            for i in range(14):
                msg = mido.Message('control_change', control=i, value=0)
                self.outport.send(msg)
                self.mute_list[i] = 0
        except Exception as e:
            self.display_label.setText(f"MuteAll Error: {e}")

    def setSolo(self, index):
        try:
            if not self.outport:
                self.display_label.setText("MIDI port not open for setSolo")
                return
            # Mute all first
            self.muteAll()
            # Unmute the solo
            msg = mido.Message('control_change', control=index, value=127)
            self.outport.send(msg)
            self.mute_list[index] = 1
        except Exception as e:
            self.display_label.setText(f"SetSolo Error: {e}")

    def setParam(self):
        # Your parameter setting logic here, no hardware access so no exception wrapping needed
        self.display_label.setText("Parameters set")

    def setPath(self):
        try:
            path = QFileDialog.getExistingDirectory(self, "Select Project Directory", os.getcwd())
            if path:
                self.projectpath = path
                self.display_label.setText(f"Project path set: {path}")
        except Exception as e:
            self.display_label.setText(f"Set Path Error: {e}")

    def cancelRec(self):
        self.cancel = 1
        self.display_label.setText("Cancel requested")

    def sequenceMaster(self):
        try:
            # This is a placeholder for your sequence master logic.
            # Use try-except inside if needed.
            self.getMIDIDevice()
            self.getAudioDevice()
            self.loop_time = self.bar_input.value() * 4 * 60 / float(self.bpm_input.text())
            self.pattern_nr = self.patterns_input.value()

            self.start_Rec()
            self.stop_MIDI()
        except Exception as e:
            self.display_label.setText(f"SequenceMaster Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Midirecorder()
    window.show()
    sys.exit(app.exec())
