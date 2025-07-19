# Underbridge OP-Z multichannel exporter
# Copyright 2022 Thomas Herrmann Email: herrmann@raise-uav.com
# NiceGUI version 2025

import mido
import pyaudio
import wave
import time
import threading
import os
from nicegui import ui, app
from pathlib import Path


class Midirecorder:
    def __init__(self):
        # Initialize variables
        self.op_device = []
        self.audio_device = []
        self.loop_time = 0
        self.inport = 0
        self.outport = 0
        self.path = 0
        self.folder = 0
        self.pattern_nr = 0
        self.j = 0       
        self.addsec = 0
        self.projectpath = 0
        self.cancel = 0
        self.RATE = 0
        self.mute_list = [0] * 14  # Midi mute selection of all 14 necessary channels
        
        # UI state variables
        self.mode_select = 3  # Default to Pattern mode (3)
        self.displaymsg = "Welcome to Underbridge"
        self.modifier_values = [False] * 6  # For the 6 modifier checkboxes
        
        # Create the UI
        self.create_ui()
        
    def create_ui(self):
        # Set dark theme
        ui.dark_mode().enable()
        
        # Main container
        with ui.column().classes('w-full max-w-3xl mx-auto p-4').style('background-color: #565A5E'):
            ui.label('Underbridge OP-Z multichannel exporter').classes('text-xl text-center mb-4')
            
            # Parameter section
            with ui.card().classes('w-full mb-4').style('background-color: #444'):
                ui.label('Parameter').classes('text-lg text-white')
                
                with ui.grid(columns=3).classes('w-full gap-2'):
                    ui.input('Name', value='Name').bind_value(self, 'name_input')
                    ui.input('BPM', value='BPM').bind_value(self, 'bpm_input')
                    
                    with ui.column():
                        ui.label('Nr. Bars')
                        ui.slider(min=1, max=9, value=1, step=1).bind_value(self, 'bar_input')
                    
                    with ui.column():
                        ui.label('Patterns')
                        ui.slider(min=1, max=16, value=16, step=1).bind_value(self, 'patterns_input')
                    
                    with ui.column():
                        ui.label('Extra Sec')
                        ui.slider(min=0, max=10, value=0, step=1).bind_value(self, 'add_sec')
            
            # Exclude Modifiers section
            with ui.card().classes('w-full mb-4').style('background-color: #444'):
                ui.label('Exclude Modifiers').classes('text-lg text-white')
                
                with ui.grid(columns=6).classes('w-full'):
                    for i, name in enumerate(["Send 1", "Send 2", "Tape", "Master", "Perform", "Module"]):
                        ui.checkbox(name).bind_value(self, f'modifier_values[{i}]')
            
            # Mode selection
            with ui.card().classes('w-full mb-4').style('background-color: #444'):
                ui.radio(['Project', 'Pattern'], value='Pattern', on_change=self.update_mode)
            
            # Control buttons
            with ui.row().classes('w-full justify-around mb-4'):
                ui.button('Set Prmtr', on_click=self.setParam).props('color=blue')
                ui.button('Directory', on_click=self.setPath).props('color=blue')
                ui.button('RECORD', on_click=lambda: threading.Thread(target=self.sequenceMaster).start()).props('color=red')
                ui.button('CANCEL', on_click=self.cancelRec).props('color=orange')
            
            # Status display
            self.display = ui.label(self.displaymsg).classes('w-full p-2 text-center mb-4').style('background-color: lightgrey; color: black')
            
            # Tutorial
            ui.label('Enter Parameter, then press set Param, choose directory and start recording').classes('w-full p-2 text-center mb-4').style('background-color: grey; color: white')
            
            # Footer
            ui.label('donate <3 @ https://link.raise-uav.com').classes('text-center w-full')
    
    def update_mode(self, e):
        self.mode_select = 2 if e.value == "Project" else 3
    
    def update_modifier(self, index):
        # This will be called when a modifier checkbox changes
        pass
    
    def getMIDIDevice(self):   
        device_list = mido.get_output_names()
        print(device_list)
        try: 
            self.op_device = list(filter(lambda x: 'OP-Z' in x, device_list))        
            self.op_device = self.op_device[0]
            self.displaymsg = "OP-Z found"
            self.display.text = self.displaymsg
        except:
            self.displaymsg = "Can´t find OP-Z : MIDI Error."
            self.display.text = self.displaymsg

    def getAudioDevice(self):
        p = pyaudio.PyAudio()
        try:
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            for i in range(0, numdevices):
                if "OP-Z" in p.get_device_info_by_host_api_device_index(0, i).get('name') and (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    self.audio_device = i
            print("Detected OP-Z audio at Index:", self.audio_device, p.get_device_info_by_host_api_device_index(0, self.audio_device).get('name'))
        except:
            self.displaymsg = "OP-Z Audio Device not found."
            self.display.text = self.displaymsg

        try:         
            devinfo = p.get_device_info_by_index(self.audio_device)  
            test = p.is_format_supported(48000, input_device=devinfo['index'], input_channels=devinfo['maxInputChannels'], input_format=pyaudio.paInt16)
            self.RATE = 48000
            print("48kHz")
        except:
            self.RATE = 44100
            print("44100kHz compatibility mode")    

    def getBPM(self):        
        inport = mido.open_input(self.op_device)
        msg = inport.poll(self)

    def setLoop(self):       
        try:        
            bpm = self.bpm_input
            bar = self.bar_input
            addsec = self.add_sec
            self.loop_time = (240 / int(bpm) * int(bar)) + int(addsec)
            print("Loop time set!", self.loop_time)
            self.displaymsg = "BPM Set!"
            self.display.text = self.displaymsg
        except Exception as e:
            print(f"Error setting loop: {e}")
            self.displaymsg = "Please enter accurate BPM."
            self.display.text = self.displaymsg

    def setParam(self):
        self.setLoop()

    def openMidi(self):    
        self.outport = mido.open_output(self.op_device)    

    def setProject(self, projnr):
        msg = mido.Message('program_change', song=self.projnr, program=1)
        self.outport.send(msg)

    def muteAll(self):        
        checkbutton_name = 0    
        
        for j in range(0, 8):
            self.mute_list[j] = 1     
        
        for i in range(0, 6):
            self.mute_list[i+8] = 1 if self.modifier_values[i] else 0

        for k in range(0, 14):
            msg = mido.Message('control_change', control=53, channel=k, value=self.mute_list[k])
            self.outport.send(msg)

    def setSolo(self, chn):        
        msg = mido.Message('control_change', control=53, channel=chn, value=0)        
        self.outport.send(msg)
        
    def start_MIDI(self):        
        msg = mido.Message('start')
        self.outport.send(msg)
        self.displaymsg = "Playback started"
        self.display.text = self.displaymsg

    def stop_MIDI(self):        
        msg = mido.Message('stop')
        self.outport.send(msg)
        self.displaymsg = "Playback stopped"
        self.display.text = self.displaymsg

    def unmuteAll(self):        
        for i in range(0, 15):
            msg = mido.Message('control_change', control=53, channel=i, value=0)
            self.outport.send(msg)        

    def nextPattern(self):        
        msg = mido.Message('control_change', control=103, value=16)
        self.outport.send(msg)
        self.displaymsg = "Next Pattern"
        self.display.text = self.displaymsg

    def nextSong(self):
        pass

    def closeMidi(self):           
        self.outport.close()    
        self.displaymsg = "MIDI closed"
        self.display.text = self.displaymsg

    async def setPath(self):
        folder = self.name_input
        # Use NiceGUI's file dialog
        try:
            result = await ui.run_javascript('window.showDirectoryPicker().then(dir => dir.name)')
            if result:
                path = result
                self.displaymsg = "Directory set!"
                self.display.text = self.displaymsg
                self.makeDir(path, folder)
        except Exception as e:
            print(f"Error setting path: {e}")
            self.displaymsg = "Error selecting directory"
            self.display.text = self.displaymsg

    def makeDir(self, path, folder):
        self.projectpath = os.path.join(path, folder)
        try:    
            os.mkdir(self.projectpath)   
        except:
            self.displaymsg = "Directory Error. Please enter different Name."
            self.display.text = self.displaymsg

    def makeDirNr(self, pattern_nr):    
        try:
            os.mkdir(os.path.join(self.projectpath, str(pattern_nr))) 
        except:
            self.displaymsg = "Directory Error"
            self.display.text = self.displaymsg

    def start_Rec(self):
        self.displaymsg = "Recording..."
        self.display.text = self.displaymsg
        CHUNK = 128
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        
        RECORD_SECONDS = self.loop_time
        WAVE_OUTPUT_FILENAME = f"{self.name_input}_track{self.j+1}.wav"
        
        p = pyaudio.PyAudio()   
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index=self.audio_device,
                        frames_per_buffer=CHUNK                        
                        )
        
        frames = []
        self.start_MIDI()
        for i in range(0, int(self.RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if self.mode_select == 2:
            output_path = os.path.join(self.projectpath, str(self.pattern_nr), WAVE_OUTPUT_FILENAME)
        else:
            output_path = os.path.join(self.projectpath, WAVE_OUTPUT_FILENAME)
            
        wf = wave.open(output_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        self.j = self.j + 1
        if self.j == 8:
            self.j = 0
        self.displaymsg = "End of Recording"
        self.display.text = self.displaymsg

    def sequenceMaster(self):       
        self.cancel = 0
        self.getMIDIDevice()
        time.sleep(1)
        self.getAudioDevice()
        self.displaymsg = "Sequence started"
        self.display.text = self.displaymsg
        try:        
            self.openMidi()                            
            if self.mode_select == 2:
                self.makeDirNr(self.pattern_nr)            

            for i in range(0, 8): 
                pattern_limit = self.patterns_input.value 
                if self.cancel == 1 or self.pattern_nr == pattern_limit:
                    break
                self.muteAll()                
                time.sleep(0.1)
                self.setSolo(i)
                self.start_Rec()               
                self.stop_MIDI()
                time.sleep(1)
                self.unmuteAll()
                time.sleep(1)                
                mode = self.mode_select                
                
                if i == 7 and mode == 2: 
                    time.sleep(5)
                    self.nextPattern()
                    self.pattern_nr += 1
                    if self.pattern_nr == 15:
                        self.pattern_nr = 0
                    self.sequenceMaster()
        except Exception as e:
            print(f"Error: {e}")
            self.displaymsg = "OP-Z Sequence error try restarting the OP-Z or press CANCEL Button"
            self.display.text = self.displaymsg

    def cancelRec(self):      
        self.j = 0
        self.cancel = 1  
        self.closeMidi()


# Initialize the app
def main():
    app.on_startup(lambda: ui.notify('Underbridge started'))
    
    # Create the recorder instance
    underbridge = Midirecorder()
    
    # Run the app
    ui.run(
        title='Underbridge',
        port=12000,
        host='0.0.0.0',
        reload=False,
        show=False,
        favicon='logo.ico',
        storage_secret='underbridge-secret'
    )


if __name__ == "__main__":
    main()