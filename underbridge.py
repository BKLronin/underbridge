# Underbridge OP-Z multichannel exporter
# Copyright 2022 Thomas Herrmann Email: herrmann@raise-uav.com

import mido
import pyaudio
import wave
from tkinter import *
from tkinter import filedialog as fd
import time
import threading
import os

device_list = []
op_device = []
audio_device = []
loop_time = 0
inport = 0
outport = 0
path = 0
folder = 0
pattern_nr = 0
j = 0
mode_select=0
addsec = 0
projectpath = 0
cancel = 0
RATE = 0


def getMIDIDevice():   
    global device_list
    global op_device
    device_list = mido.get_output_names()
    print (device_list)
    try: 
        op_device = list(filter(lambda x: 'OP-Z' in x, device_list))        
        op_device = op_device[0]
        print (op_device)
        displaymsg.set("OP-Z found")
    except:
        displaymsg.set("Can´t find OP-Z : MIDI Error.")

def getAudioDevice():
    global audio_device
    global RATE
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
                audio_device = i
        #audio_device = 4           
        print ("Detected OP-Z audio at Index:",audio_device, p.get_device_info_by_host_api_device_index(0, audio_device).get('name'))
    except:
        displaymsg.set("OP-Z Audio Device not found.")

    devinfo = p.get_device_info_by_index(audio_device)  
    try:         
        devinfo = p.get_device_info_by_index(audio_device)  
        test = p.is_format_supported(48100, input_device=devinfo['index'], input_channels=devinfo['maxInputChannels'],input_format=pyaudio.paInt16)
        RATE = 48000
        print("48kHz")
    except:
        RATE = 44100
        print("44100kHz compatibility mode")    

def getBPM():
    global op_device
    inport= mido.open_input(op_device)
    msg = inport.poll()
    #print(msg)

def setLoop():
    global loop_time
    try:
        bpm = bpm_input.get()
        bar = bar_input.get()
        addsec = add_sec.get()
        loop_time = (240 / int(bpm) * int(bar)) + int(addsec)
        print("Loop time set!")
        displaymsg.set("BPM Set!")
    except:
        displaymsg.set("Please enter accurate BPM.")
    return time

def setParam():
    setLoop()
    #mode = mode_select.get()
    #if mode == 2:
    #    projnr = project_input.get()
    #    setProject(projnr)

def openMidi():    
    global outport  
    global op_device
    outport= mido.open_output(op_device)    
    #displaymsg.set("OP-Z MIDI not connected :(")
    print(outport) 

def setProject(projnr):
    global outport
    msg= mido.Message('program_change',song= projnr, program = 1)
    outport.send(msg)

def muteAll():
    global outport
    for i in range (0,15):
        msg = mido.Message('control_change',control= 53, channel= i, value=1)
        outport.send(msg)
        
def setSolo(chn):
    global outport
    msg = mido.Message('control_change',control= 53, channel= chn, value=0)
    outport.send(msg)

def start_MIDI():
    global outport
    msg = mido.Message('start')
    outport.send(msg)
    displaymsg.set("Playback started")

def stop_MIDI():
    global outport
    msg = mido.Message('stop')
    outport.send(msg)
    displaymsg.set("Playback stopped")

def unmuteAll():
    global outport
    for i in range (0,15):
        msg = mido.Message('control_change',control= 53, channel= i, value=0)
        outport.send(msg)        

def nextPattern():
    global outport
    msg = mido.Message('control_change', control = 103, value = 16)
    outport.send(msg)
    displaymsg.set("Next Pattern")

def nextSong():
    pass

def closeMidi():    
    global outport
    outport.close()    
    displaymsg.set("MIDI closed")     

def setPath():
    global path
    folder = name_input.get()
    path = fd.askdirectory()    
    displaymsg.set("Directory set!")
    makeDir()

def makeDir():
    global folder
    global projectpath
    folder = name_input.get()
    projectpath = path + '/' + folder
    try:    
        os.mkdir(projectpath)   
    except:
        displaymsg.set("Directory Error. Please enter different Name.")

def makeDirNr(pattern_nr):    
    global projectpath    
    #Pfad wird addiert deswegen zusätzliche verzeichnisse
    #projectpath = projectpath + '/' + str(pattern_nr)
    try:
        os.mkdir(projectpath + '/' + str(pattern_nr)) 
    except:
        displaymsg.set("Directory Error")
    #print(projectpath)

def start_Rec():
    displaymsg.set("Recording...")
    global path
    global time
    global j
    global pro
    global pattern_nr
    global audio_device
    global RATE

    CHUNK = 128
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    #RATE = 44100
    RECORD_SECONDS = loop_time
    WAVE_OUTPUT_FILENAME =  name_input.get()+ "_" + "track" + str(j+1) + ".wav"
    
    p = pyaudio.PyAudio()   
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index= audio_device,
                    frames_per_buffer=CHUNK
                    
                    )

    #print("* recording")
    
    frames = []
    start_MIDI()
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    #print("Done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
    if mode_select.get() == 2:
        wf = wave.open(projectpath + '/' + str(pattern_nr) + '/' + WAVE_OUTPUT_FILENAME, 'wb')
    else:
        wf = wave.open(projectpath + '/' + WAVE_OUTPUT_FILENAME, 'wb')

    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    j = j + 1
    if j == 8:
        j= 0
    displaymsg.set("End of Recording")

def sequenceMaster():
    
    global cancel
    global pattern_nr
    cancel = 0
    #print("test")

    getMIDIDevice()
    time.sleep(1)
    getAudioDevice()

    displaymsg.set("Sequence started")

    try:        
        openMidi()
            
        if mode_select.get() == 2:
            makeDirNr(pattern_nr)    

        for i in range (0,8): #
            pattern_limit = patterns_input.get() 
            if cancel == 1 or pattern_nr == pattern_limit:
                break
            #print("sequence started",i)       
            muteAll()
            time.sleep(0.1)
            setSolo(i)
            #starting Midi during wave record for timing        
            start_Rec()       
            #print(i)
            stop_MIDI()
            time.sleep(1)
            unmuteAll()
            mode = mode_select.get()                
            
            if i == 7 and mode == 2: 
                #print(mode_select)            
                time.sleep(5)
                nextPattern()
                pattern_nr += 1
                if pattern_nr == 9 :
                    pattern_nr = 0
                sequenceMaster()
    except:
        displaymsg.set("OP-Z Sequence error try restarting the OP-Z or press CANCEL Button")

def cancelRec():
    global cancel
    global outport
    global j
    j = 0
    cancel = 1  
    closeMidi()

#GUI Main
buttonsize_x = 7
buttonsize_y = 2
mode_select = 0

root = Tk()
root.title('underbridge for OP-Z')
root.resizable(width=False, height=False) #565A5E
root.tk_setPalette(background='#565A5E', foreground='black',activeBackground='#283867', activeForeground='black' )

upperframe= LabelFrame(root, text= "Parameter",padx= 10, pady =2, fg = 'white')
upperframe.grid(row = 0, column = 0, padx =2, pady =2,)

lowerframe= Frame(root,padx= 10, pady =5)
lowerframe.grid(row = 1, column = 0, padx =2, pady =2)

footer= Frame(root,padx= 15, pady =2)
footer. grid(row = 2, column = 0, padx =2, pady =2)

mode_select = IntVar()
displaymsg = StringVar()
#root.geometry('550x150+0+0')

Get_BPM = Button(upperframe, text="Get BPM",width = buttonsize_x, height = buttonsize_y, fg = 'lightgrey', command = lambda:getBPM())

#ALL = Radiobutton(lowerframe, text= 'ALL', value = 1 , variable = mode_select, width = buttonsize_x, height = buttonsize_y , indicatoron = 0, bg= '#1b7d24' )
Song = Radiobutton(lowerframe, text= 'Project', value = 2 , variable = mode_select, width = buttonsize_x, height = buttonsize_y , indicatoron = 0, bg= '#1b7d24' )
Pattern = Radiobutton(lowerframe, text= 'Pattern', value = 3 , variable = mode_select, width = buttonsize_x, height = buttonsize_y, indicatoron = 0,bg= '#1b7d24' )
Pattern.select()

bar_input = Scale(upperframe, from_ = 1, to = 4, orient = HORIZONTAL, label="Nr. Bars", sliderlength= 10, length= 75, fg = 'white')
#bar_text = Label(upperframe,text="Nr. of Bars", width = 8, height = 1)

patterns_input = Scale(upperframe, from_ = 1, to = 10, orient = HORIZONTAL, label="Patterns",sliderlength= 10, length= 75, fg = 'white')
patterns_input.set(value=10)

bpm_input = Entry(upperframe, width =10, text="BPM",bg= 'lightgrey', relief= FLAT)
#bpm_text = Label(upperframe,text="BPM", width = 8, height = 1)
bpm_input.insert(0, "BPM")

#project_input = Entry(upperframe, width =10, text="Project",bg= 'white')
#bpm_text = Label(upperframe,text="BPM", width = 8, height = 1)
#project_input.insert(0, "Project Nr.")

add_sec = Scale(upperframe, from_ = 0, to = 10, orient = HORIZONTAL, label="extra Sec", sliderlength= 10, length= 75, fg = 'white')
#add_text = Label(upperframe,text="Sec offset", width = 8, height = 1)

name_input = Entry(upperframe, width =10, text="Name",bg = 'lightgrey', relief= FLAT)
name_input.insert(0, "Name")
#name_text = Label(upperframe,text="Prj Name", width = 8, height = 1)

set_param = Button(lowerframe, text="Set Prmtr",width = buttonsize_x, height = buttonsize_y, fg = 'white',bg= '#0095FF', command = lambda:setParam())
set_path = Button(lowerframe, text="Directory",width = buttonsize_x, height = buttonsize_y,fg = 'white',bg= '#0095FF', command = lambda:setPath())
start_recording = Button(lowerframe, text="RECORD",width = buttonsize_x, height = buttonsize_y,fg = 'white', bg = '#FF2200', command = lambda:threading.Thread(target = sequenceMaster).start())

tutorial = Label(footer,text="Enter Parameter, then press set Param, choose directory and start recording", height = 2, bg ='grey',fg= 'white', relief = FLAT)
display = Label(lowerframe,textvariable= displaymsg,width = 60, height = buttonsize_y -1, bg ='lightgrey', relief = FLAT)

cancel = Button(lowerframe,text = "CANCEL" , width = buttonsize_x, height = buttonsize_y, bg ='#FFCC00', fg= 'white', command = lambda: cancelRec())
cancel.grid(row = 0, column = 6, padx =2, pady =2)

donate = Label(footer, text= "donate <3 @ https://link.raise-uav.com", height = 1)
donate.grid(row = 3, column = 4, padx =2, pady =10, columnspan=2)


#Get_BPM.grid(row = 1, column = 0, padx =2, pady =2)

#ALL.grid()
Song.grid(row = 0, column = 1, padx =5, pady =2)
Pattern.grid(row = 0, column = 2, padx =5, pady =2)

name_input.grid(row = 0, column = 0, padx =5, pady =0)
#name_text.grid(row = 1, column = 2, padx =0, pady =0)

bpm_input.grid(row = 0, column = 1, padx =5, pady =0)
#bpm_text.grid(row = 0, column = 0, padx =0, pady =0)

#project_input.grid(row = 0, column = 2, padx =5, pady =0)

bar_input.grid(row = 0, column = 3, padx =5, pady =2)
#bar_text.grid(row = 1, column = 2, padx =0, pady =0)

patterns_input.grid(row = 0, column = 4, padx =5, pady =2)

add_sec.grid(row = 0, column = 5, padx =5, pady =2)
#add_text.grid(row = 1, column = 0, padx =0, pady =0)

set_param.grid(row = 0, column = 3, padx =5, pady =2)
set_path.grid(row = 0, column = 4, padx =5, pady =2)
start_recording.grid(row = 0, column = 5, padx =5, pady =2)

tutorial.grid(row = 1, column = 0, padx =5, pady =5, columnspan=5)
display.grid(row = 1, column = 0, padx =2, pady =10, columnspan= 7)

root.mainloop()