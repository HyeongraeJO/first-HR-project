# Reading wave file
# show MEAN and MAX value for every 1s
# as text and plot

from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

# 읽기
path  = "C:/Users/MELAB/Desktop/sedtest/"
fname = "AUD_18_17_43.wav"

fs, data = wavfile.read(path + fname)   # fs is the sampling rate
ns = int(data.shape[0] / fs)            # ns is the duration in seconds
print(fs, ns, data.shape)

da_time = np.zeros(ns)
da_mean = np.zeros(ns)
da_max = np.zeros(ns)
          
# 1초씩
for i in range(ns):
    ndata = data[i*fs:(i+1)*fs-1]
    da_mean[i] = np.average(np.abs(ndata))
    da_max[i] = np.max(np.abs(ndata))
    da_time[i] = i    

i=0
for i in range(ns):
    print(da_time[i], int(da_mean[i]), da_max[i])
    
plt.plot(da_time, da_mean, label="MEAN of ABS")
plt.plot(da_time, da_max, label="MAX of ABS")
plt.legend()
plt.xlabel("Time [s]")
plt.ylabel("SP with 40 dB")
plt.show()