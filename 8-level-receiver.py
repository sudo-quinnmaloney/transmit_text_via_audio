
# coding: utf-8

# In[91]:

import numpy as np
import pyaudio
import struct
import matplotlib.pyplot as plt


# In[92]:

frequency_dict = [{'000':1200, '001':1300, '010':1400, '011':1500, '100':1600, '101':1700, '110':1800, '111':1900}, {'000':2200, '001':2300, '010':2400, '011':2500, '100':2600, '101':2700, '110':2800, '111':2900}]
frequency_dict_inv = [{v: k for k, v in channel.items()} for channel in frequency_dict]

Fbit = 10 #bit frequency
Fs = 44100 #sampling frequency
A = 1 #amplitude of the signal
FREQ_THRESHOLD = 30 #must be smaller than Fdev

CHUNK = 1024
RECORD_SECONDS = 50
CHANNELS = 1
FORMAT = pyaudio.paInt16

BARKER = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1]
BARKER = BARKER + BARKER
TEST = "_t_"
#TEST_LEN = len(TEST)*(Fs//Fbit)*3
TEST_LEN = int(len(TEST)*Fs/Fbit*8/3)


# In[93]:

def fft(sig):
    return np.abs(np.fft.rfft(sig))


# In[94]:

def index_freq(f) :
    return round(f/Fbit)


# In[95]:

def fft_plot(ns):
    yf = np.abs(np.fft.rfft(ns))
    plt.plot(yf[index_freq(1000):index_freq(2000)])
    plt.grid()
    plt.show()


# In[96]:

def content_at_freq(fft_sample, f, Fbit) :
    lower = f-FREQ_THRESHOLD
    upper = f+FREQ_THRESHOLD
    indexFreqs = [index_freq(f) for f in range(lower,upper, 1)]
    freqSample = max([fft_sample[index] for index in indexFreqs])
    return freqSample


# In[97]:

def filtered(sig, choice, full):
    data = []
    if(full):
        x = len(sig)//(Fs//Fbit)*(Fs//Fbit)
    else :
        x = TEST_LEN
    for i in range(0,x,Fs//Fbit):
        bit = sig[i:i+Fs//Fbit]
        bitfft = fft(bit)
        
        xData = [content_at_freq(bitfft, level, Fbit) for level in frequency_dict_inv[choice].keys()]
        
        toAppend = list(frequency_dict_inv[choice][list(frequency_dict_inv[choice].keys())[np.argmax(xData)]])
        for n in toAppend:
            data.append(int(n))
            
    return data


# In[98]:

def decode_letter(letter):
    binary = int("0b"+letter,base=2)
    m = ""
    try :
        m = binary.to_bytes((binary.bit_length() + 7) // 8, 'big').decode() #decoding from built-in functions in python
    except (UnicodeDecodeError) :
        m = False
    return m


# In[99]:

def decode(bin_text):
    str_text = "".join([ str(c) for c in bin_text])
    string = ""
    for i in range(0,len(str_text),8):
        letter = decode_letter(str_text[i:i+8])
        if(letter != False):
            string += letter
        if len(string)>len(TEST) and string[len(string)-len(TEST):]==TEST:
            #print('This happened.')
            return string[:len(string)-len(TEST)]
    return string


# In[100]:

def fromstring_buffer(buffer) :
    return struct.unpack('%dh' % (len(buffer)/2), buffer)


# In[101]:

def process_raw(in_data):
    data = np.array(fromstring_buffer(in_data))
    return data


# In[102]:

def listen_to_signal():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,rate=Fs, input=True,frames_per_buffer=CHUNK)
    frames = []
    stream.start_stream()

    for i in range(0, int(Fs / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        data = process_raw(data)
        frames.append(data)
        
    stream.stop_stream()
    stream.close()
    audio.terminate()
    return np.hstack(frames)


# In[103]:

def modulation(choice,bin_text):
    t = np.arange(0,1/float(Fbit),1/float(Fs), dtype=np.float)
    signal = np.ndarray(len(bin_text)//3*len(t),dtype=np.float)
    
    i=0
    for j in range(0,len(bin_text),3):
        bits = ''.join([str(n) for n in bin_text[j:j+3]])
        signal[i:i+len(t)] = A * np.cos(2*np.pi*(frequency_dict[choice][bits])*t)
        i += len(t)
        
    return signal


# In[104]:

def double_cosinus(bin_text):
    cos0 = modulation(0,bin_text)
    cos1 = modulation(1,bin_text)
    return cos0 + cos1


# In[105]:

def get_sync_signal():
    return double_cosinus(BARKER)


# In[106]:

def try_sync(sig):
    sync_signal = get_sync_signal()
    sync_padded = np.hstack((sync_signal, np.zeros(sig.size-sync_signal.size)))
    correlation = np.abs(np.fft.ifft(np.fft.fft(sig) * np.conj(np.fft.fft(sync_padded))))
    return np.argmax(correlation)


# In[107]:

def sync(sig):
    SYNC = False
    i=0
    x = len(get_sync_signal())
    index = 0
    while not SYNC:
        chunk = sig[i:i+(5*Fs)]
        index = try_sync(chunk)
        if index + x < len(chunk):
             SYNC = True
        i += x
    return sig[index+x:]


# In[108]:

import time
def receiver():
    ls = listen_to_signal()
    x = sync(ls)
    
    t0 = decode(filtered(x,0,False))
    t1 = decode(filtered(x,1,False))
    x = x[TEST_LEN:]
    print(t0)
    print(t1)
    if(t0 == TEST):
        return decode(filtered(x,0,True))
    if(t1 == TEST):
        return decode(filtered(x,1,True))
    else:
        print("Fatal Error !")

# In[20]:

def main():
    x = receiver()
    print(x)

if __name__ == "__main__":
    main()

