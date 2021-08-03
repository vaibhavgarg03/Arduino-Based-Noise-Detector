import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
import pyfirmata


board = pyfirmata.Arduino('COM3')

red_led = board.digital[11]
red_led.mode = pyfirmata.PWM

green_led = board.digital[9]
green_led.mode = pyfirmata.PWM

blue_led = board.digital[10]
blue_led.mode = pyfirmata.PWM

RATE = 44100 # Hz
fpb = int(RATE/10)

def RGB_color(red_light_value, green_light_value, blue_light_value):
    red_led.write(red_light_value*0.60)
    green_led.write(green_light_value*0.60)
    blue_led.write(blue_light_value*0.60)

p = pa.PyAudio()

stream = p.open(
    format = pa.paInt16,
    channels = 1,
    rate = RATE,
    input=True,
    output=True,
    frames_per_buffer=fpb
)


fig1, td = plt.subplots(1)
x = np.arange(0,2*fpb,2)
line_td, = td.plot(x, np.random.rand(fpb),'g')
td.set_title("Oscilloscope")
td.set_ylim(-25000,25000)
td.set_xlim(0,fpb)
td.set_yticks([20000,-20000,15000,-15000,8000,-8000,1000,-1000,0])
td.set_yticklabels( ["Dangerous","Dangerous","Harmful","Harmful","Safe","Safe","Low","Low","Inaudible"])
td.set_xlabel('Frames per Buffer', horizontalalignment='center')
td.set_ylabel('Loudness')
fig2, fd= plt.subplots(1)
x_fd = np.linspace(0, RATE, fpb)
line_fd, = fd.semilogx(x_fd, np.random.rand(fpb), 'r')
fd.set_title("Spectrum Analyzer")
fd.set_xlim(20,RATE/2)
fd.set_ylim(0,1)
fd.set_yticks([1,0.8,0.6,0.4,0.2,0])
fd.set_yticklabels( ["Dangerous","Harmful","Loud","Safe","Low","Inaudible"])
fd.set_xlabel('Frequency', horizontalalignment='center')
fd.set_ylabel('Loudness')
fig1.show()
fig2.show()

while True:
    data = stream.read(fpb)
    data_Int = struct.unpack(str(fpb) + 'h', data)
    data_Int1 = np.asarray(data_Int)
    if any(data_Int1 > 20000) or any(data_Int1 < -20000):
        RGB_color(1, 0, 0) # Red
    elif (any(data_Int1 > 15000) and any(data_Int1 < 20000)) or (any(data_Int1 < -15000) and any(data_Int1 > -20000)):
        RGB_color(0, 0, 1) # Blue
    elif (any(data_Int1 > 8000) and any(data_Int1 < 15000)) or (any(data_Int1 < -8000) and any(data_Int1 > -15000)):
        RGB_color(1, 0.49, 0) # Yellow
    elif (any(data_Int1 > 1000) and any(data_Int1 < 8000)) or (any(data_Int1 < -1000) and any(data_Int1 > -8000)):
        RGB_color(0, 1, 0) # Green
    elif (any(data_Int1 > 100) and any(data_Int1 < 1000)) or (any(data_Int1 < -100) and any(data_Int1 > -1000)):
        RGB_color(1, 0.118, 0.196) # Raspberry
    else:
        RGB_color(1, 1, 1) # White
    line_td.set_ydata(data_Int)
    line_fd.set_ydata(np.abs(np.fft.fft(data_Int))*2/(11000*fpb))
    fig1.canvas.draw()
    fig1.canvas.flush_events()
    fig2.canvas.draw()
    fig2.canvas.flush_events()
    print(max(data_Int1),min(data_Int1))
