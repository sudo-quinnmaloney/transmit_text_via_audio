
# coding: utf-8

# In[1]:

import numpy as np
import scipy.io.wavfile as sc
import soundfile as sf
import sounddevice as sd
import sys


# In[21]:

frequency_dict = [{'000':1200, '001':1300, '010':1400, '011':1500, '100':1600, '101':1700, '110':1800, '111':1900}, {'000':2200, '001':2300, '010':2400, '011':2500, '100':2600, '101':2700, '110':2800, '111':2900}]
Fbit = 10 #bit frequency
Fs = 44100 #sampling frequency
A = 1 #amplitude of the signal

BARKER = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1]
BARKER = BARKER + BARKER
TEST = "_t_"


# In[3]:

def encode(text):
    int_text = int.from_bytes(text.encode(), 'big')
    bin_text = str(bin(int_text))
    bin_text = [0] + [int(d) for d in bin_text[2:]] #take out the b from the binary string"
    return bin_text


# In[4]:

def modulation(choice,bin_text):
    t = np.arange(0,1/float(Fbit),1/float(Fs), dtype=np.float)
    signal = np.ndarray(len(bin_text)//3*len(t),dtype=np.float)
    
    i=0
    for j in range(0,len(bin_text),3):
        bits = ''.join([str(n) for n in bin_text[j:j+3]])
        signal[i:i+len(t)] = A * np.cos(2*np.pi*(frequency_dict[choice][bits])*t)
        i += len(t)
        
    return signal


# In[5]:

def double_cosinus(bin_text):
    cos0 = modulation(0,bin_text)
    cos1 = modulation(1,bin_text)
    return cos0 + cos1


# In[6]:

def get_sync_signal():
    return double_cosinus(BARKER)


# In[7]:

def get_test_signal():
    return double_cosinus(encode(TEST))


# In[8]:

def emitter_real(text):
    modul = double_cosinus(encode(text))
    sync = get_sync_signal()
    test = get_test_signal()
    return np.append(np.append(np.append(sync,np.append(test,modul)),test), test)


# In[13]:

def emitter(filepath):
    with open(filepath, "r") as data:
        x = emitter_real(data.read())
        sc.write("emitter2b_expanded.wav",Fs,x)
        #samples, samplerate = sf.read('emitter2b_expanded.wav')
        #sd.play(samples, samplerate)
        sd.wait()


# In[14]:

def main():
    path = 'test162.txt'
    emitter(path)

if __name__ == "__main__":
    main()

