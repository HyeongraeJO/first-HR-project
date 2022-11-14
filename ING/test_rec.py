# Record sound in blocking mode in PC with soundcard
# save as wave file
# start and stop cmmand from keyboards

import pyaudio
import wave
import keyboard
import time
        
CHUNK = 1024              # about 1/15 s
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 1800      # max 30 min = 1800 s

def recording():
    global st
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if keyboard.is_pressed("f"):
            print("Finished")
            break
    
    print(int(i*CHUNK/RATE))    # recording duration in seconds
   
    stream.stop_stream()
    stream.close()
    p.terminate()

    now = time.localtime()
    WAVE_OUTPUT_FILENAME = "C:/Users/MELAB/Desktop/sedtest/AUD_%02d_%02d_%02d" % (now.tm_hour, now.tm_min, now.tm_sec) +".wav"    
 
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# main 시작
print("#############################################")
print("s for start, f for finish!")
print("#############################################")

# 버튼 대기
while True:
    if keyboard.is_pressed("s"):
        print("Started,,,")
        recording()
    if keyboard.is_pressed("f"):
        print("FIN")
        break