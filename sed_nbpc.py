# SED Sound based Event Detector for SAFE_HOME
# Monitoring and Deployment of DNN model
# [input] water related sound from microphone in bathroom
# [output1] For each frame (1/30 s), probablity among [WASHING, FLUSHING, SHOWERING]
# [output2] For 1 seconds, [WASHING, FLUSHING, SHOWERING, OTHERS]
# [output3] timestamp and log of event when there was sound
# LOG in FireBase https://safe-home-uou-default-rtdb.firebaseio.com/

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time 
from random import *
import threading
import pyaudio
import numpy as np

#import keyboard

# Firebase database 인증 및 앱 초기화 # .json의 위치경로를 정확하게 !
# 파이어베이스 realtime database 프로젝트의 고유 URL
# json file이 다른 폴더에 있으면 아래와 같이
# cred = credentials.Certificate('C:/Users/MELAB/Desktop/sedtest/safe-home-uou-firebase-adminsdk-ukla0-f94c1a433c.json')
cred = credentials.Certificate('safe-home-uou-firebase-adminsdk-ukla0-f94c1a433c.json')

firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://safe-home-uou-default-rtdb.firebaseio.com/' 
})

# 큰 소음(사고)의 기준값 : 마이크 게인 40dB 에서 평균 2000 이상
global TH_EM
TH_EM = 2000
 
# 행동 물소리 소음 기준값 : 마이크 게인 40dB 에서 평균 100 ~ 2000 
global TH_ACT
TH_ACT = 100 

# Flag is set when every 1 second 
global f_ready
f_ready = 0 

global dact
dact = ["SHOWERING", "WASHING", "FLUSHING", "OTHERS" ]

global data
data = []

CHUNK = 16000    # 한 번에 읽어오는 단위, 1초간의 데이터
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000     # sampling rate
SAMPLE_SIZE = 2  # FORMAT의 바이트 수

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# 쓰레드 1초 동안 사운드카드에서 소리를 변수 data로 읽어온다.  
# 진행중일 때는 f_ready = 0, 끝나면 플래그 f_ready = 1
def th_read():
    global f_ready
    global data
  
    data = stream.read(CHUNK)

    f_ready = 1
    return 

def ksj():
    act_rand = randint(0,3)
    return act_rand

threading.Timer(0, th_read).start()

while(True):
    if f_ready == 1:                    # 1초동안의 녹음이 끝났으면... 
        f_ready = 0                     # 다음 1초 녹음을 바로 시작시켜놓고
        threading.Timer(0, th_read).cancel()
        threading.Timer(0, th_read).start()
                                        # 평균 음압을 계산하여
        frame = np.frombuffer(data, dtype=np.int16)
        SPL = int(np.average(np.abs(frame)))
        print("Sound Level MEAN ABS between 0 and 32767 : ", SPL)
        now = time.localtime()

        if SPL > TH_EM:                   # 샤우팅이면
            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print("SHOUTING\n")

            ref = db.reference()          # DATABASE 기록
            ref = db.reference('DailyActs/%04d-%02d-%02d'% (now.tm_year, now.tm_mon, now.tm_mday)) #경로가 없으면 생성
            ref.update({"%02d:%02d:%02d" % (now.tm_hour, now.tm_min, now.tm_sec) : 'EMERGENCY'})
                                        # LOCAL에 LOG FILE 기록 (추후 구현)

        elif SPL > TH_ACT:              # Activity 레벨 범위 이면 # Detected Event 서버저장
            dact_c = ksj()
            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print(dact[dact_c], "\n")
            
            ref = db.reference()        # DB에 LOG 저장
            ref = db.reference('DailyActs/%04d-%02d-%02d'% (now.tm_year, now.tm_mon, now.tm_mday)) #경로가 없으면 생성
            ref.update({"%02d:%02d:%02d" % (now.tm_hour, now.tm_min, now.tm_sec) : dact[dact_c]})
                                        # LOCAL에 LOG FILE 기록, 날자별 파일 생성, 이벤트별 한 줄씩 추가

        else:                           # Activity 레벨 보다 작으면... 패스
            print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
            print("nothing, 's' for STOP !\n")

 #   if keyboard.is_pressed("s"):        # s를 누르면 닫고 끝낸다...
 #       print("\nSTOP\n")
 #       stream.stop_stream()
 #       stream.close()
 #       p.terminate()
 #       break
 ########