import mido
import pyaudio
import wave
from tkinter import *
from tkinter import filedialog as fd
import time
import threading
import os

loop_time = 0
inport = 0
outport = 0
path = 0
folder = 0
j = 0
mode_select=0
addsec = 0

def getMIDIDevice():
    pass


def getBPM():
    inport= mido.open_input('OP-Z:OP-Z MIDI 1 20:0')
    msg = inport.poll()
    print(msg)

def setLoop():
    global loop_time
    bpm = bpm_input.get()
    bar = bar_input.get()
    addsec = add_sec.get()
    loop_time = (240 / int(bpm) * int(bar)) + int(addsec)
    print("Loop time set!")
    displaymsg.set("BPM Set!")
    return time

def setParam():
    setLoop()
    mode = mode_select.get()
    if mode == 2:
        projnr = project_input.get()
        setProject(projnr)

def openMidi():    
    global outport          
    outport= mido.open_output('OP-Z:OP-Z MIDI 1 20:0')
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

def nextPattern():
    global outport
    msg = mido.Message('control_change', control = 103, value = 16)
    outport.send(msg)
    displaymsg.set("Next Pattern")

def nextSong():
    pass

def closeMidi():
    pass

def setPath():
    global path
    folder = name_input.get()
    path = fd.askdirectory()    
    displaymsg.set("Directory set")
    makeDir()

def makeDir():
    global folder
    folder = name_input.get()
    os.mkdir(folder)

def start_Rec():
    displaymsg.set("Recording...")
    global path
    global time
    global j
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = loop_time
    WAVE_OUTPUT_FILENAME =  name_input.get()+ "_" + "track" + str(j+1) + ".wav"
    
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                    )

    print("* recording")
    start_MIDI()
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(path + '/'+ folder + '/' + WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    j = j + 1
    displaymsg.set("End of Recording")

def sequenceMaster():
    print("test")
    

    for i in range (0,8):
        print("sequence started",i)
        displaymsg.set("Sequence started")
        openMidi()
        muteAll()
        setSolo(i)
        #starting Midi during wave record for timing        
        start_Rec()
        #print(i)
        stop_MIDI()
        mode = mode_select.get()        
        if i == 7 and mode == 2: 
            print(mode_select)
            stop_MIDI()
            time.sleep(5)
            nextPattern()
            sequenceMaster()      
            

#GUI Main
buttonsize_x = 8
buttonsize_y = 2
mode_select = 0

root = Tk()
root.title('underbridge for OP-Z')
root.resizable(width=False, height=False) #565A5E
root.tk_setPalette(background='#565A5E', foreground='black',activeBackground='#283867', activeForeground='black' )

upperframe= LabelFrame(root, text= "Parameter",padx= 10, pady =10, fg = 'white')
upperframe.grid(row = 0, column = 0, padx =2, pady =2, columnspan=7)

lowerframe= Frame(root,padx= 15, pady =10)
lowerframe.grid(row = 1, column = 0, padx =2, pady =2, columnspan=7)

mode_select = IntVar()
displaymsg = StringVar()
#root.geometry('550x150+0+0')

Get_BPM = Button(upperframe, text="Get BPM",width = buttonsize_x, height = buttonsize_y, fg = 'white', command = lambda:getBPM())

#ALL = Radiobutton(lowerframe, text= 'ALL', value = 1 , variable = mode_select, width = buttonsize_x, height = buttonsize_y , indicatoron = 0, bg= '#1b7d24' )
Song = Radiobutton(lowerframe, text= 'Project', value = 2 , variable = mode_select, width = buttonsize_x, height = buttonsize_y , indicatoron = 0, bg= '#1b7d24' )
Pattern = Radiobutton(lowerframe, text= 'Pattern', value = 3 , variable = mode_select, width = buttonsize_x, height = buttonsize_y, indicatoron = 0,bg= '#1b7d24' )
Pattern.select()

bar_input = Scale(upperframe, from_ = 1, to = 4, orient = HORIZONTAL, label="Nr. Bars", sliderlength= 10, length= 75, fg = 'white')
#bar_text = Label(upperframe,text="Nr. of Bars", width = 8, height = 1)

patterns_input = Scale(upperframe, from_ = 1, to = 10, orient = HORIZONTAL, label="Patterns",sliderlength= 10, length= 75, fg = 'white')

bpm_input = Entry(upperframe, width =10, text="BPM",bg= 'white')
#bpm_text = Label(upperframe,text="BPM", width = 8, height = 1)
bpm_input.insert(0, "BPM")

#project_input = Entry(upperframe, width =10, text="Project",bg= 'white')
#bpm_text = Label(upperframe,text="BPM", width = 8, height = 1)
#project_input.insert(0, "Project Nr.")

add_sec = Scale(upperframe, from_ = 0, to = 10, orient = HORIZONTAL, label="extra Sec", sliderlength= 10, length= 75, fg = 'white')
#add_text = Label(upperframe,text="Sec offset", width = 8, height = 1)

name_input = Entry(upperframe, width =10, text="Name",bg = 'white')
name_input.insert(0, "Name")
#name_text = Label(upperframe,text="Prj Name", width = 8, height = 1)

set_param = Button(lowerframe, text="set Param",width = buttonsize_x, height = buttonsize_y, fg = 'white',bg= 'blue', command = lambda:setParam())
set_path = Button(lowerframe, text="Directory",width = buttonsize_x, height = buttonsize_y,fg = 'white',bg= 'blue', command = lambda:setPath())
start_recording = Button(lowerframe, text="Record",width = buttonsize_x, height = buttonsize_y,fg = 'white', bg = 'red', command = lambda: threading.Thread(target = sequenceMaster()).start())

tutorial = Label(root,text="Enter Parameter, then press set_length, choose directory and start recording", width = 75, height = 2, bg ='grey',fg= 'white', relief = SUNKEN)
display = Label(root,textvariable= displaymsg, width = 75, height = 2, bg ='white', relief = SUNKEN)


#Get_BPM.grid(row = 1, column = 0, padx =2, pady =2)

#ALL.grid(row = 1, column = 0, padx =5, pady =2)
Song.grid(row = 1, column = 1, padx =5, pady =2)
Pattern.grid(row = 1, column = 2, padx =5, pady =2)

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

set_param.grid(row = 1, column = 3, padx =5, pady =10)
set_path.grid(row = 1, column = 4, padx =5, pady =10)
start_recording.grid(row = 1, column = 5, padx =5, pady =10)

tutorial.grid(row = 2, column = 0, padx =2, pady =10, columnspan=7)
display.grid(row = 3, column = 0, padx =2, pady =2, columnspan=7)

root.mainloop()