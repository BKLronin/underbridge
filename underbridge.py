# Underbridge OP-Z multichannel exporter
# Copyright 2022 Thomas Herrmann Email: herrmann@raise-uav.com

import mido
import pyaudio
import wave
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk
import time
import threading
import os


class Midirecorder:
    def __init__(self):

        self.window = Tk()
        self.window.title('underbridge')
        self.window.resizable(width=False, height=False) #565A5E
        self.window.tk_setPalette(background='#565A5E', foreground='black',activeBackground='#283867', activeForeground='black' )
        #device_list = []
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
        self.mute_list =[0] * 14 #Midi mute selection of all 14 necessary channels
        #modifier_dict = {"mod1": modifier1_va}

        #GUI Main
        self.buttonsize_x = 7
        self.buttonsize_y = 2
       
        self.mode_select = IntVar()
        self.displaymsg = StringVar()
        self.modifier1_value = IntVar()
        self.modifier2_value = IntVar()
        self.modifier3_value = IntVar()
        self.modifier4_value = IntVar()
        self.modifier5_value = IntVar()
        self.modifier6_value = IntVar()

        upperframe= LabelFrame(self.window, text= "Parameter",padx= 10, pady =2, fg = 'white')
        upperframe.grid(row = 0, column = 0, padx =2, pady =2,)

        lowerframe= Frame(self.window,padx= 10, pady =5)
        lowerframe.grid(row = 2, column = 0, padx =2, pady =2)

        modifiers = LabelFrame(self.window, text= "Exclude Modifiers",padx= 10, pady =2, fg = 'white')
        modifiers.grid(row = 1, column = 0, padx =2, pady =2)

        footer= Frame(self.window,padx= 15, pady =2)
        footer. grid(row = 3, column = 0, padx =2, pady =2)

        #Get_BPM = Button(upperframe, text="Get BPM",width = self.buttonsize_x, height = self.buttonsize_y, fg = 'lightgrey', command = getBPM)
        Song = Radiobutton(lowerframe, text= 'Project', value = 2 , variable = self.mode_select, width = self.buttonsize_x, height = self.buttonsize_y , indicatoron = 0, bg= '#1b7d24' )
        Pattern = Radiobutton(lowerframe, text= 'Pattern', value = 3 , variable = self.mode_select, width = self.buttonsize_x, height = self.buttonsize_y, indicatoron = 0,bg= '#1b7d24' )
        Pattern.select()

        self.bar_input = Scale(upperframe, from_ = 1, to = 4, orient = HORIZONTAL, label="Nr. Bars", sliderlength= 10, length= 75, fg = 'white')
        self.patterns_input = Scale(upperframe, from_ = 1, to = 10, orient = HORIZONTAL, label="Patterns",sliderlength= 10, length= 75, fg = 'white')
        self.patterns_input.set(value=10)
        self.bpm_input = Entry(upperframe, width =10, text="BPM",bg= 'lightgrey', relief= FLAT)        
        self.bpm_input.insert(0, "BPM")
        self.add_sec = Scale(upperframe, from_ = 0, to = 10, orient = HORIZONTAL, label="extra Sec", sliderlength= 10, length= 75, fg = 'white')
        
        self.name_input = Entry(upperframe, width =10, text="Name",bg = 'lightgrey', relief= FLAT)
        self.name_input.insert(0, "Name")  

        modifier1 = Checkbutton(modifiers, text="Send 1", variable=self.modifier1_value)
        modifier1.grid(row = 0, column = 0, padx =5, pady =2)

        modifier2 = Checkbutton(modifiers,text="Send 2", variable=self.modifier2_value)
        modifier2.grid(row = 0, column = 1, padx =5, pady =2)

        modifier3 = Checkbutton(modifiers,text="Tape",variable=self.modifier3_value )
        modifier3.grid(row = 0, column = 2, padx =5, pady =2)

        modifier4 = Checkbutton(modifiers,text="Master", variable= self.modifier4_value)
        modifier4.grid(row = 0, column = 3, padx =5, pady =2)

        modifier5 = Checkbutton(modifiers,text="Perform", variable= self.modifier5_value)
        modifier5.grid(row = 0, column = 4, padx =5, pady =2)

        modifier6 = Checkbutton(modifiers,text="Module", variable=self.modifier6_value)
        modifier6.grid(row = 0, column = 5, padx =5, pady =2)

        set_param = Button(lowerframe, text="Set Prmtr",width = self.buttonsize_x, height = self.buttonsize_y, fg = 'white',bg= '#0095FF', command = self.setParam)
        set_path = Button(lowerframe, text="Directory",width = self.buttonsize_x, height = self.buttonsize_y,fg = 'white',bg= '#0095FF', command = self.setPath)
        start_recording = Button(lowerframe, text="RECORD",width = self.buttonsize_x, height = self.buttonsize_y,fg = 'white', bg = '#FF2200', command = lambda:threading.Thread(target = self.sequenceMaster).start())

        tutorial = Label(footer,text="Enter Parameter, then press set Param, choose directory and start recording", height = 2, bg ='grey',fg= 'white', relief = FLAT)
        display = Label(lowerframe,textvariable= self.displaymsg,width = 60, height = self.buttonsize_y -1, bg ='lightgrey', relief = FLAT)

        cancel = Button(lowerframe,text = "CANCEL" , width = self.buttonsize_x, height = self.buttonsize_y, bg ='#FFCC00', fg= 'white', command =self.cancelRec)
        cancel.grid(row = 0, column = 6, padx =2, pady =2)

        donate = Label(footer, text= "donate <3 @ https://link.raise-uav.com", height = 1)
        donate.grid(row = 3, column = 4, padx =2, pady =10, columnspan=2)
       
        Song.grid(row = 0, column = 1, padx =5, pady =2)
        Pattern.grid(row = 0, column = 2, padx =5, pady =2)

        self.name_input.grid(row = 0, column = 0, padx =5, pady =0)
        self.bpm_input.grid(row = 0, column = 1, padx =5, pady =0)
        self.bar_input.grid(row = 0, column = 3, padx =5, pady =2)
        self.patterns_input.grid(row = 0, column = 4, padx =5, pady =2)
        self.add_sec.grid(row = 0, column = 5, padx =5, pady =2)
        
        set_param.grid(row = 0, column = 3, padx =5, pady =2)
        set_path.grid(row = 0, column = 4, padx =5, pady =2)
        start_recording.grid(row = 0, column = 5, padx =5, pady =2)

        tutorial.grid(row = 1, column = 0, padx =5, pady =5, columnspan=5)
        display.grid(row = 1, column = 0, padx =2, pady =10, columnspan= 7)

        self.window.mainloop()

    def getMIDIDevice(self):   
        #global device_list
        #global op_device
        device_list = mido.get_output_names()
        print (device_list)
        try: 
            self.op_device = list(filter(lambda x: 'OP-Z' in x, device_list))        
            self.op_device = self.op_device[0]
            print (self.op_device)
            self.displaymsg.set("OP-Z found")
        except:
            self.displaymsg.set("Can´t find OP-Z : MIDI Error.")

    def getAudioDevice(self):
        #global audio_device
        #global RATE
        p = pyaudio.PyAudio()
        try:
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            for i in range(0, numdevices):
                #audio_device = p.get_device_info_by_host_api_device_index(0, i).get('name')
                if "OP-Z" in p.get_device_info_by_host_api_device_index(0, i).get('name') and (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    self.audio_device = i
            #audio_device = 4           
            print ("Detected OP-Z audio at Index:",self.audio_device, p.get_device_info_by_host_api_device_index(0, self.audio_device).get('name'))
        except:
            self.displaymsg.set("OP-Z Audio Device not found.")

        #devinfo = p.get_device_info_by_index(self.audio_device)  
        try:         
            devinfo = p.get_device_info_by_index(self.audio_device)  
            test = p.is_format_supported(48000, input_device=devinfo['index'], input_channels=devinfo['maxInputChannels'],input_format=pyaudio.paInt16)
            self.RATE = 48000
            print("48kHz")
        except:
            self.RATE = 44100
            print("44100kHz compatibility mode")    

    def getBPM(self):        
        inport= mido.open_input(self.op_device)
        msg = inport.poll(self)
        #print(msg)

    def setLoop(self):       
        try:        
            bpm = self.bpm_input.get()
            bar = self.bar_input.get()
            addsec = self.add_sec.get()
            self.loop_time = (240 / int(bpm) * int(bar)) + int(addsec)
            print("Loop time set!", self.loop_time)
            self.displaymsg.set("BPM Set!")
        except:
            self.displaymsg.set("Please enter accurate BPM.")
        #return self.loop_time

    def setParam(self):
        self.setLoop()
        #mode = mode_select.get()
        #if mode == 2:
        #    projnr = project_input.get()
        #    setProject(projnr)

    def openMidi(self):    
        #global outport  
        #global op_device
        self.outport= mido.open_output(self.op_device)    
        #displaymsg.set("OP-Z MIDI not connected :(")
        print(self.outport) 

    def setProject(self,projnr):
        msg= mido.Message('program_change',song= self.projnr, program = 1)
        self.outport.send(msg)

    def muteAll(self):        
        checkbutton_name = 0    
        print(self.mute_list)
        
        for j in range (0,7):
            self.mute_list[j] = 1     
        
        for i in range (1,6):
            checkbutton_name = 'self.modifier{}_value'.format(i)     #checkbutton 1- 6         
            self.mute_list[i+7] = eval(checkbutton_name).get()       #9th position in mute list  

        for k in range (0,13):
            msg = mido.Message('control_change',control= 53, channel= k, value= self.mute_list[k])
            self.outport.send(msg)
        print("Muted Channels",self.mute_list)

    def setSolo(self,chn):        
        msg = mido.Message('control_change',control= 53, channel= chn, value=0)        
        self.outport.send(msg)
        
    def start_MIDI(self):        
        msg = mido.Message('start')
        self.outport.send(msg)
        self.displaymsg.set("Playback started")
        print("midi")

    def stop_MIDI(self):        
        msg = mido.Message('stop')
        self.outport.send(msg)
        self.displaymsg.set("Playback stopped")

    def unmuteAll(self):        
        for i in range (0,15):
            msg = mido.Message('control_change',control= 53, channel= i, value=0)
            self.outport.send(msg)        

    def nextPattern(self):        
        msg = mido.Message('control_change', control = 103, value = 16)
        self.outport.send(msg)
        self.displaymsg.set("Next Pattern")

    def nextSong(self):
        pass

    def closeMidi(self):           
        self.outport.close()    
        self.displaymsg.set("MIDI closed")     

    def setPath(self):
        #global path
        folder = self.name_input.get()
        path = fd.askdirectory()    
        self.displaymsg.set("Directory set!")
        self.makeDir(path,folder)

    def makeDir(self,path,folder):
        #global folder
        #global projectpath
        #folder = name_input.get()
        self.projectpath = path + '/' + folder
        try:    
            os.mkdir(self.projectpath)   
        except:
            self.displaymsg.set("Directory Error. Please enter different Name.")

    def makeDirNr(self, pattern_nr):    
        #global projectpath    
        #Pfad wird addiert deswegen zusätzliche verzeichnisse
        #projectpath = projectpath + '/' + str(pattern_nr)
        try:
            os.mkdir(self.projectpath + '/' + str(pattern_nr)) 
        except:
            self.displaymsg.set("Directory Error")
        #print(projectpath)

    def start_Rec(self):
        print("record")
        self.displaymsg.set("Recording...")
        CHUNK = 128
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        
        RECORD_SECONDS= self.loop_time
        print("record")
        WAVE_OUTPUT_FILENAME =  self.name_input.get() + "_" + "track" + str(self.j+1) + ".wav"       
        print(WAVE_OUTPUT_FILENAME)
        p = pyaudio.PyAudio()   
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index= self.audio_device,
                        frames_per_buffer=CHUNK                        
                        )

        print("* recording")
        
        frames = []
        self.start_MIDI()
        for i in range(0, int(self.RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        #print("Done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()
        if self.mode_select.get() == 2:
            wf = wave.open(self.projectpath + '/' + str(self.pattern_nr) + '/' + WAVE_OUTPUT_FILENAME, 'wb')
        else:
            wf = wave.open(self.projectpath + '/' + WAVE_OUTPUT_FILENAME, 'wb')

        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        self.j = self.j + 1
        if self.j == 8:
            self.j= 0
        self.displaymsg.set("End of Recording")

    def sequenceMaster(self):       
        self.cancel = 0
        self.getMIDIDevice()
        time.sleep(1)
        self.getAudioDevice()
        self.displaymsg.set("Sequence started")
        try:        
            self.openMidi()                            
            if self.mode_select.get() == 2:
                self.makeDirNr(self.pattern_nr)            

            for i in range (0,8): 
                pattern_limit = self.patterns_input.get() 
                if self.cancel == 1 or self.pattern_nr == pattern_limit:
                    break
                #print("sequence started",i)       
                self.muteAll()
                
                time.sleep(0.1)
                self.setSolo(i)
                #starting Midi during wave record for timing                     
                self.start_Rec()               
                self.stop_MIDI()
                time.sleep(1)
                self.unmuteAll()
                mode = self.mode_select.get()                
                
                if i == 7 and mode == 2: 
                    #print(mode_select)            
                    time.sleep(5)
                    self.nextPattern()
                    self.pattern_nr += 1
                    if self.pattern_nr == 9 :
                        self.pattern_nr = 0
                    self.sequenceMaster()
        except:
            self.displaymsg.set("OP-Z Sequence error try restarting the OP-Z or press CANCEL Button")

    def cancelRec(self):      
        self.j = 0
        self.cancel = 1  
        self.closeMidi()

    
underbridge = Midirecorder()