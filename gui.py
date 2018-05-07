# -*- coding: utf-8 -*-
"""
Created on Thu May 18 17:13:32 2017

@author: S Vinu Sankar
"""

import tkinter as tk
import tkinter.filedialog
from scipy.io import wavfile as wf
import numpy as np
import sounddevice as sd
import time
from PIL import ImageTk, Image
from tkinter import messagebox

''' <---- Scaling functions ----> '''

output, x, Fs = 0, 0, 0
location = ''
scale, rate = 0.1, 0
perform_func = 0
t1 = 0
T = 0
t = 0
rec_a, rt1, rt2 = [], 0, 0

def TSM(ts, play = 1):
    
    global x, Fs, output, location, T, t1, rate
    try:
        Fs, x = wf.read(location)
        rate = Fs
        
        if len(x.shape) > 1:
            x = np.array([x[i][0] for i in range(len(x))])
            
        L = len(x)
        T = L/Fs
            
        ft_size = int(Fs * 30 / 1000)
        hop_size = int(ft_size / 4)
        
        time_scale = ts
        ang  = np.zeros(ft_size)
        raw_out = np.zeros(ft_size, dtype=complex)
        output = np.zeros(int(L/time_scale) + ft_size, dtype = complex)
        window = np.hanning(ft_size)
        
        step = 0
        d = 0
        
        while L - (ft_size + hop_size) > step:
        
        
            stepp = int(step)
            sig1 =  np.fft.fft(window * x[stepp: stepp + ft_size])
            sig2 =  np.fft.fft(window * x[stepp + hop_size: stepp + ft_size + hop_size])
            
            ang += (np.angle(sig2) - np.angle(sig1))
            
            
            raw_out.real, raw_out.imag = np.cos(ang), np.sin(ang)
            
            output[d: d + ft_size] += window * np.fft.ifft(np.abs(sig2) * raw_out)
            d += hop_size
            step += hop_size * time_scale
        
        if max(x) < 1:
            output = np.array(output*max(x)/max(output), dtype = 'float32')
    
        else:
            output = np.array(output*max(x)/max(output), dtype = 'int16')
                
        if play:
            t1 = time.time()
            sd.play(output, Fs)
    
    except:
        messagebox.showerror('File Error', 'Choose a valid audio .wav file')
        
def PSM(ps, play = 1):
    
    global Fs, output, t1, rate
    
    pitch_scale = ps
    TSM(1.0 / pitch_scale, 0)
    rate = int(Fs * pitch_scale)
    t1 = time.time()
    if play:
        sd.play(output, rate)
    
''' <----- GUI code -----> '''

def Browse():
    
    global root, location, lct
    
    location = lct.get() 
    root.filename = tkinter.filedialog.askopenfilename()
    location = root.filename        
    lct.delete(0, tk.END)
    lct.insert(tk.END, location)
    

def SCale(var):
    
    global sscale, scale, T, t1, t, output
    scale = sscale.get()    
    t2 = time.time()
        
    if t1 != 0:
        t += t2-t1
        t1 = time.time()        
        sd.stop()
        
        if perform_func == 'ps' and t < T:
            PSM(scale, 0)
            sd.play(output[int(len(output)*(t)/T*0.75): ], Fs*scale)
            
        elif perform_func == 'ts':
            TSM(scale, 0)
            sd.play(output[int(len(output)*(t)/T*0.75): ], Fs)
            
        if t >= T:
            t = 0

def setts():
    
    global perform_func
    perform_func = 'ts'

def setps():
    
    global perform_func
    perform_func = 'ps'

def perform():
    
    global scale, perform_func
    
    if perform_func == 'ts':
        TSM(scale)
        
    elif perform_func == 'ps':
        PSM(scale)

def Stoprec():
    
    global rec_a, location, r2, rt1
    
    rt2 = time.time()
    sd.stop()
    wf.write('output.wav', 16000, rec_a[:int((rt2-rt1)/60*len(rec_a))])
    location = 'output.wav'
    
       
def Startrec():
    
    global rec_a, r2, rt1
    
    rt1 = time.time()
    rec_a = sd.rec(frames=16000*60, samplerate=16000, channels=1, mapping=[2], blocking=False)
 
def Save():

    global output, savel, rate
    
    saveloc = savel.get()
    
    if '.wav' in saveloc:
        saveloc = saveloc[:-4]
        
    wf.write('Records/'+saveloc+'.wav', rate, output)
       

root = tk.Tk()
root.iconbitmap(r'pv1.ico')
root.title('Phase Vocoder')
root.resizable(False, False)
img = ImageTk.PhotoImage(Image.open("phasevocoder.png"))


panel = tk.Label(root, image = img, width = 440)
panel.pack(side = tk.TOP)

# frame 1

frame1 = tk.Frame(root, borderwidth = 1, relief = tk.SUNKEN)
frame1.pack(side = tk.TOP)

select_file = tk.Label(frame1, text = 'Select WAV file:')
select_file.pack(side = tk.LEFT, padx = 10, pady = 5)

lct = tk.Entry(frame1, width = 40)
lct.insert(tk.END, 'Browse/Type file directory...')
lct.pack(side = tk.LEFT, padx = 10, pady = 5)

browse = tk.Button(frame1, text = 'Browse', command = Browse)
browse.pack(side = tk.LEFT, padx = 10, pady = 5)

# frame 4

frame4 = tk.Frame(root, borderwidth = 1, relief = tk.SUNKEN, width = 300)
frame4.pack(side = tk.TOP)

record = tk.Label(frame4, text = 'Record audio:')
record.pack(side = tk.LEFT, padx = 15, pady = 5)
start = tk.Button(frame4, text = 'Start', width = 18, command = Startrec)
stop = tk.Button(frame4, text = 'Stop', width = 18, command = Stoprec)
start.pack(side = tk.LEFT, padx = 15, pady = 7)
stop.pack(side = tk.LEFT, padx = 15, pady = 7)

# frame 2

frame2 = tk.Frame(root, borderwidth = 1, relief = tk.SUNKEN, width = 300)
frame2.pack(side = tk.TOP)

select_perform = tk.Label(frame2, text = 'Perform:')
select_perform.pack(side = tk.LEFT, padx = 29, pady = 5)
rb1 = tk.Radiobutton(frame2, text = 'Time scaling', value = 1, indicatoron = 0, width = 18, command = setts)
rb2 = tk.Radiobutton(frame2, text = 'Pitch Scaling', value = 2, indicatoron = 0, width = 18, command = setps)
rb1.pack(side = tk.LEFT, padx = 15, pady = 7)
rb2.pack(side = tk.LEFT, padx = 15, pady = 7)

# frame 3

frame3 = tk.Frame(root, borderwidth = 1, relief = tk.SUNKEN)
frame3.pack(side = tk.TOP)

sscale = tk.Scale(frame3, command = SCale, from_ = 0.1, to = 5.0, length = 250, sliderlength = 20, orient = tk.HORIZONTAL, resolution = 0.1)
sscale.pack(side = tk.LEFT, padx = 15, pady = 5)
sscale.set(0.1)

perform = tk.Button(frame3, text = 'Scale', width = 6, command = perform)
perform.pack(side = tk.LEFT, padx = 15, pady = 5)

stop1 = tk.Button(frame3, text = 'Stop', width = 5, command = Stoprec)
stop1.pack(side = tk.LEFT, padx = 15, pady = 5)

# frame 5

frame5 = tk.Frame(root, borderwidth = 1, relief = tk.SUNKEN)
frame5.pack(side = tk.TOP)

savel = tk.Entry(frame5, width = 33)
savel.pack(side = tk.LEFT, padx = 5)
savel.insert(tk.END, 'Save file name...')

save = tk.Button(frame5, text = 'Save scaled audio', command = Save, padx = 5, pady = 10, width = 30)
save.pack(side = tk.LEFT)

def on_closing():
    sd.stop()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
