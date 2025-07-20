from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLineEdit, QRadioButton, QSlider, QCheckBox,
    QFrame, QFileDialog
)

from PySide6.QtCore import Qt, Signal
import mido
import pyaudio
import wave
import threading
import time
import os

from PySide6.QtCore import QTimer



class Midirecorder(QWidget):
    status_changed = Signal(str)
    def __init__(self):
        super().__init__()
        self.projectpath = None
        self.loop_time = None
        self.outport = None
        self.setWindowTitle('underbridge')
        self.setFixedSize(600, 500)  # Similar to original window size
        self.setStyleSheet("""
        /* === Base Widget Styles === */
        QWidget {
            background-color: #1e1e1e;
            color: #f8f8f2;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }

        /* === Group Boxes === */
        QGroupBox {
            background-color: transparent;
            border: 1px solid #ff9966;
            border-radius: 8px;
            margin-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
            color: #ffcc99;
            font-weight: bold;
        }

        /* === Labels === */
        QLabel {
            color: #f8f8f2;
            background: transparent;
            font-size: 14px;
        }

        /* === Line Edit === */
        QLineEdit {
            background-color: #1e1e1e;
            border: 1px solid #ff9966;
            border-radius: 5px;
            padding: 6px 10px;
            color: #f8f8f2;
            font-size: 14px;
        }

        /* === Buttons === */
        QPushButton {
            background-color: #ff9966;
            color: #1e1e1e;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #ffaa77;
        }

        QPushButton:pressed {
            background-color: #ff8844;
        }

        /* === Sliders === */
        QSlider::groove:horizontal {
            border: 1px solid #444;
            height: 8px;
            background: #3c3c3c;
            margin: 2px 0;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #ffaa77;
            border: 1px solid #ff9966;
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }

        /* === Checkboxes === */
        QCheckBox {
            spacing: 5px;
            font-size: 14px;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #ff9966;
            border-radius: 3px;
            background: #1e1e1e;
        }

        QCheckBox::indicator:checked {
            background-color: #ffaa77;
            border: 1px solid #ffaa77;
        }

        /* === Radio Buttons === */
        QRadioButton {
            font-size: 14px;
        }

        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #ff9966;
            border-radius: 8px;
            background: #1e1e1e;
        }

        QRadioButton::indicator:checked {
            background-color: #ffaa77;
            border: 1px solid #ffaa77;
        }

        /* === Links (footer) === */
        QLabel:hover {
            color: #ffe0b3;
        }

        a {
            color: #ffcc99;
            text-decoration: none;
        }

        a:hover {
            color: #ffe0b3;
            text-decoration: underline;
        }

        /* === Tooltips === */
        QToolTip {
            background-color: #ffaa77;
            color: #1e1e1e;
            border: none;
            padding: 6px;
            border-radius: 5px;
        }

        /* === Frame/Footer === */
        QFrame {
            background-color: transparent;
        }
        """)

        self.j = 0
        self.pattern_nr = 0
        self.cancel = False

        self.mute_list = [0] * 14  # MIDI mute selection of all 14 necessary channels
        self.RATE = 0

        # Layout setup
        layout = QGridLayout()
        layout.alignment().AlignCenter
        self.setLayout(layout)


        self.create_upperframe(layout)
        self.create_modifiers_frame(layout)
        self.create_lowerframe(layout)
        self.create_footer(layout)

        self.status_changed.connect(self.update_display)

    def update_display(self, text):
        self.displaymsg.setText(text)

    def create_upperframe(self, layout):
        upperframe = QGroupBox("Parameter")
        upper_layout = QGridLayout()
        upperframe.setLayout(upper_layout)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")

        self.bpm_input = QLineEdit()
        self.bpm_input.setPlaceholderText("120")

        self.bar_input = QSlider(Qt.Horizontal)
        self.bar_input.setRange(1, 10)
        self.bar_input.setValue(1)

        self.bar_nr = QLabel("1")

        self.patterns_input = QSlider(Qt.Horizontal)
        self.patterns_input.setRange(1, 16)
        self.patterns_input.setValue(1)  # Default value

        self.ptr_nr = QLabel("1")

        self.add_sec = QSlider(Qt.Horizontal)
        self.add_sec.setRange(0, 10)

        self.extra_nr = QLabel("1")

        upper_layout.addWidget(QLabel("Name"), 0, 0)
        upper_layout.addWidget(self.name_input, 0, 1)

        upper_layout.addWidget(QLabel("BPM"), 0, 3)
        upper_layout.addWidget(self.bpm_input, 0, 4)

        upper_layout.addWidget(QLabel("Nr. Bars"), 1, 0)
        upper_layout.addWidget(self.bar_input, 1, 1)
        upper_layout.addWidget(self.bar_nr, 1,2)

        upper_layout.addWidget(QLabel("Patterns"), 1, 3)
        upper_layout.addWidget(self.patterns_input, 1, 4)
        upper_layout.addWidget(self.ptr_nr, 1, 5)

        upper_layout.addWidget(QLabel("extra Sec"), 3, 0)
        upper_layout.addWidget(self.add_sec, 3, 1)
        upper_layout.addWidget(self.extra_nr, 3, 2)
        
        self.bar_input.valueChanged.connect(self.update_bar)
        self.patterns_input.valueChanged.connect(self.update_ptrn)
        self.add_sec.valueChanged.connect(self.update_extra)
        
        layout.addWidget(upperframe, 0, 0)

    def update_bar(self, value):
        self.bar_nr.setText(str(value))

    def update_ptrn(self, value):
        self.ptr_nr.setText(str(value))

    def update_extra(self, value):
        self.extra_nr.setText(str(value))

    def create_modifiers_frame(self, layout):
        modifiers = QGroupBox("Exclude Modifiers")
        mod_layout = QGridLayout()
        modifiers.setLayout(mod_layout)

        self.modifier_values = [QCheckBox(f"Send {i+1}") for i in range(6)]
        self.modifier_values[0].setText("Send 1")
        self.modifier_values[1].setText("Send 2")
        self.modifier_values[2].setText("Tape")
        self.modifier_values[3].setText("Master")
        self.modifier_values[4].setText("Perform")
        self.modifier_values[5].setText("Module")

        for idx, cb in enumerate(self.modifier_values):
            mod_layout.addWidget(cb, 0, idx)

        layout.addWidget(modifiers, 1,0)

    def create_lowerframe(self, layout):
        lowerframe = QGroupBox("Execute")
        lower_layout = QGridLayout()
        lowerframe.setLayout(lower_layout)
        lowerframe.alignment().AlignCenter
        #,lower_layout.setSpacing(15)

        self.mode_select = 3
        self.Song = QRadioButton("Project")
        self.Pattern = QRadioButton("Pattern")
        self.Pattern.setChecked(True)

        self.Song.toggled.connect(lambda: setattr(self, "mode_select", 2) if self.Song.isChecked() else None)
        self.Pattern.toggled.connect(lambda: setattr(self, "mode_select", 3) if self.Pattern.isChecked() else None)

        lower_layout.addWidget(self.Song, 0, 0)
        lower_layout.addWidget(self.Pattern, 0, 1)

        #set_param = QPushButton("Set Prmtr")
        #set_path = QPushButton("Directory")
        start_recording = QPushButton("RECORD")


        #lower_layout.addWidget(set_param, 0, 2)
        #lower_layout.addWidget(set_path, 0, 3)
        lower_layout.addWidget(start_recording, 0, 4)

        #set_param.clicked.connect(self.setParam)
        #set_path.clicked.connect(self.setPath)
        start_recording.clicked.connect(self.startRecording)

        layout.addWidget(lowerframe, 2, 0)

    def create_footer(self, layout):
        footer = QWidget()
        foot_layout = QVBoxLayout()
        footer.setLayout(foot_layout)

        tutorial_label = QLabel("Enter Parameter, then press RECORDING button.")
        tutorial_label.setAlignment(Qt.AlignCenter)
        tutorial_label.setStyleSheet("color: darkgrey")
        #donate_label = QLabel("<a href='https://link.raise-uav.com'>donate <3 @ https://link.raise-uav.com</a>")
        #donate_label.setOpenExternalLinks(True)

        sponsor_label = QLabel()
        sponsor_label.setOpenExternalLinks(True)
        sponsor_label.setText(
            "<a href='https://app.raise-uav.com' style='color: #ff9966; text-decoration: underline;'>"
            "Visit Sponsor </a>")
        sponsor_label.setAlignment(Qt.AlignCenter)

        self.displaymsg = QLabel()
        self.displaymsg.setAlignment(Qt.AlignCenter)

        foot_layout.addWidget(tutorial_label)
        foot_layout.addWidget(self.displaymsg)
        foot_layout.addWidget(sponsor_label)

        #foot_layout.addWidget(donate_label)
        layout.addWidget(footer, 3, 0)

    def getMIDIDevice(self):
        try:
            device_list = mido.get_output_names()
            print("Available MIDI Devices:", device_list)
            self.op_device = next((x for x in device_list if "OP-Z" in x), None)
            if self.op_device:
                self.status_changed.emit("OP-Z MIDI found")
            else:
                self.status_changed.emit("Can't find OP-Z : MIDI Error.")
        except Exception as e:
            print("MIDI Error:", e)
            self.status_changed.emit("Error accessing MIDI devices.")

    def getAudioDevice(self):
        p = pyaudio.PyAudio()
        self.audio_device = None
        try:
            for i in range(p.get_device_count()):
                dev = p.get_device_info_by_index(i)
                if "OP-Z" in dev.get('name', '') and dev.get('maxInputChannels', 0) > 0:
                    self.audio_device = i
                    break

            if self.audio_device is not None:
                devinfo = p.get_device_info_by_index(self.audio_device)
                try:
                    if p.is_format_supported(48000, input_device=devinfo['index'],
                                             input_channels=devinfo['maxInputChannels'],
                                             input_format=pyaudio.paInt16):
                        self.RATE = 48000
                    else:
                        self.RATE = 44100
                except:
                    self.RATE = 44100

                self.status_changed.emit(f"Audio device found: {devinfo['name']} at {self.RATE}Hz")
            else:
                self.status_changed.emit("OP-Z Audio Device not found.")
        except Exception as e:
            print("Audio Error:", e)
            self.status_changed.emit("Error accessing audio devices.")
        finally:
            p.terminate()

    def setLoop(self):
        try:
            bpm = int(self.bpm_input.text())
            bar = self.bar_input.value()
            addsec = self.add_sec.value()
            self.loop_time = (240 / bpm * bar) + addsec
            print("Loop time set!", self.loop_time)
            self.status_changed.emit("BPM Set!")
        except Exception as e:
            print("Loop setup error:", e)
            self.loop_time = None
            self.status_changed.emit("<span style='color: yellow;'>Please enter a valid BPM (number).</span>")

    def setParam(self):
        self.setLoop()
        # mode = mode_select.get()

    def openMidi(self):
        self.outport = mido.open_output(self.op_device)

    def setProject(self, projnr):
        msg = mido.Message('program_change', song=self.projnr, program=1)
        self.outport.send(msg)

    def muteAll(self):
        for j in range(8):
            self.mute_list[j] = 1

        for i in range(6):
            self.mute_list[i+8] = int(self.modifier_values[i].isChecked())

        for k in range(14):
            msg = mido.Message('control_change', control=53, channel=k, value=self.mute_list[k])
            self.outport.send(msg)
            time.sleep(0.1)

    def setSolo(self, chn):
        msg = mido.Message('control_change', control=53, channel=chn, value=0)
        self.outport.send(msg)

    def start_MIDI(self):
        msg = mido.Message('start')
        self.outport.send(msg)
        self.status_changed.emit("Playback started")

    def stop_MIDI(self):
        msg = mido.Message('stop')
        self.outport.send(msg)
        self.status_changed.emit("Playback stopped")

    def unmuteAll(self):
        for i in range(15):
            msg = mido.Message('control_change', control=53, channel=i, value=0)
            self.outport.send(msg)

    def nextPattern(self):
        msg = mido.Message('control_change', control=103, value=16)
        self.outport.send(msg)
        self.status_changed.emit("Next Pattern")

    def nextSong(self):
        pass

    def closeMidi(self):
        self.outport.close()
        self.status_changed.emit("MIDI closed")

    def setPath(self):
        folder = self.name_input.text()
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.projectpath = f"{path}/{folder}"
            try:
                os.makedirs(self.projectpath)
                self.status_changed.emit("Directory set!")
            except Exception as e:
                self.status_changed.emit("Directory Error. Please enter different Name.")

    def makeDir(self, path, folder):
        self.projectpath = f"{path}/{folder}"
        try:
            os.makedirs(self.projectpath)
        except Exception as e:
            self.status_changed.emit(f"{e}. Please enter different Name.")

    def makeDirNr(self, pattern_nr):
        try:
            os.makedirs(f"{self.projectpath}/{pattern_nr}")
        except Exception as e:
            self.status_changed.emit("Directory Error")

    def start_Rec(self):
        if self.audio_device is None:
            self.status_changed.emit("No audio device set.")
            return

        CHUNK = 128
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RECORD_SECONDS = self.loop_time
        WAVE_OUTPUT_FILENAME = f"{self.name_input.text()}_track{self.j + 1}.wav"

        p = pyaudio.PyAudio()
        stream = None
        try:
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=self.RATE,
                            input=True,
                            input_device_index=self.audio_device,
                            frames_per_buffer=CHUNK)

            self.start_MIDI()
            frames = []

            for _ in range(int(self.RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

            if self.mode_select == 2:
                out_path = f"{self.projectpath}/{self.pattern_nr}/{WAVE_OUTPUT_FILENAME}"
            else:
                out_path = f"{self.projectpath}/{WAVE_OUTPUT_FILENAME}"

            with wave.open(out_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(frames))

            self.status_changed.emit(f"Recording complete: {WAVE_OUTPUT_FILENAME}")
            self.j = (self.j + 1) % 8

        except Exception as e:
            print("Recording Error:", e)
            self.status_changed.emit("<span style='color: red;'>Recording failed. Check device or try again.</span>")
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()

    def sequenceMaster(self):

        self.cancel = False
        self.getMIDIDevice()
        time.sleep(1)
        self.getAudioDevice()

        if not self.audio_device:
            self.status_changed.emit("<span style='color: yellow;'>No OP-Z found try to restart both the device and the app.</span>")
            return

        try:
            self.openMidi()

            total_patterns = self.patterns_input.value()
            project_mode = self.mode_select == 2  # "Project" mode

            if project_mode:
                self.pattern_nr = 0

            for pattern_index in range(total_patterns):
                if self.cancel:
                    break

                if project_mode:
                    self.makeDirNr(pattern_index)
                    self.pattern_nr = pattern_index

                for track_index in range(8):  # Always 8 tracks per pattern
                    if self.cancel:
                        break

                    self.status_changed.emit(f"Pattern {pattern_index + 1}, Track {track_index + 1}")
                    self.muteAll()
                    time.sleep(0.1)
                    self.setSolo(track_index)
                    self.start_Rec()
                    self.stop_MIDI()
                    time.sleep(1)
                    self.unmuteAll()
                    time.sleep(1)

                if project_mode:
                    self.nextPattern()
                    time.sleep(5)



        except Exception as e:
            print("Sequence error:", e)
            self.status_changed.emit("<span style='color: red;'>Error: try restarting OP-Z or cancel.</span>")
        finally:
            self.closeMidi()
            self.status_changed.emit("<span style='color: green;'>Recording session complete.</span>")

    def startRecording(self):
        self.setLoop()
        if not self.projectpath:
            self.setPath()
        if self.projectpath and self.loop_time:
            self.status_changed.emit("Sequence started")
            threading.Thread(target=self.sequenceMaster).start()
        else:
            self.status_changed.emit("<span style='color: yellow;'>Please set parameters and a valid writable directory.</span>""")

    def cancelRec(self):
        self.j = 0
        self.cancel = True
        self.closeMidi()

if __name__ == "__main__":
    app = QApplication([])
    window = Midirecorder()
    window.show()
    app.exec()
