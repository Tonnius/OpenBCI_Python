import plugin_interface as plugintypes

import numpy as np
from scipy.signal import lfilter, butter, lfilter_zi

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time
import timeit
from threading import Thread

import cPickle as pickle

from lasagne import layers
from lasagne.updates import nesterov_momentum
from nolearn.lasagne import NeuralNet
from lasagne.objectives import aggregate, binary_crossentropy
import theano

#import sys
#sys.path.append('/home/tonnius/Git/maka/code/')
#from training import AdjustVariable

nrOfSamples = 128


def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    cutoff = [lowcut / nyq, highcut / nyq]
    b, a = butter(order, cutoff, btype="bandpass")
    return b, a
def butter_bandstop(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    cutoff = [lowcut / nyq, highcut / nyq]
    b, a = butter(order, cutoff, btype="bandstop")
    return b, a
class Plotter(Thread):
    def __init__(self):
        Thread.__init__(self)
        print "Plotter activated"
        self.inputBuff = np.zeros((nrOfSamples,16))
        self.polling_interval = 1
        fname_pretrain = "/home/tonnius/Git/maka/code/net.pickle"
        with open(fname_pretrain, 'rb') as f:
            self.net_pretrain = pickle.load(f)
        
    def run(self):
        while True:
            asArray = np.stack([xi for xi in self.inputBuff])
            reshapedDataTest = asArray.reshape((-1, 1, 16, 16))
            reshapedDataTest = reshapedDataTest.astype(np.float32)
            #print("X.shape == {}; X.min == {:.3f}; X.max == {:.3f}".format(
                #reshapedDataTest.shape, reshapedDataTest.min(), reshapedDataTest.max()))  
            pred = self.net_pretrain.predict(reshapedDataTest)
            
            sample_string = "%s\n" % (str(pred))
            #print "---------------------------------"
            print sample_string
            print "---------------------------------"        
    

            time.sleep(self.polling_interval)
            
class PluginPrint(plugintypes.IPluginExtended):
    #def __init__(self):
    
    def activate(self):
        
        self.dataBuff_uV = np.zeros((nrOfSamples,16))
        self.dataBuff_filt_uV = np.zeros((nrOfSamples,16))
        self.firstDataPoint = True
        fs = 125
        order = 4
        lowcut = 5
        highcut = 50
        #nyq = 0.5 * fs
        #cutoff = [lowcut / nyq, highcut / nyq]
        self.b, self.a = butter_bandpass(lowcut, highcut, fs, order)
        self.zi = lfilter_zi(self.b, self.a)
        
        self.b2, self.a2 = butter_bandstop(49.5, 50.5, fs, 2) #50Hz
        fig, axes = plt.subplots(16,1)
        
        lines = []
        
        for i in range(0, len(axes)):
            axes[i].set_ylim([-200, 200])
            lines.append(axes[i].plot(np.transpose(self.dataBuff_filt_uV)[i]))
            
        lines = np.squeeze(lines)
        plt.ion()
        def animate(i):
            for k in range(0, len(axes)):
                lines[k].set_ydata(np.transpose(self.dataBuff_filt_uV)[k])
            return [line for line in lines]
        
        ani = animation.FuncAnimation(fig, animate, np.arange(0, 128),
            interval=25, blit = True)
        plt.show()                

        self.plottr = Plotter()
        self.plottr.daemon = True
        
        print "Print activated"

    # called with each new sample
    def __call__(self, sample):
        if sample:
            if self.firstDataPoint == True:
                self.firstDataPoint = False #because of averaging, first point is garbage
                self.plottr.start()
            else:
                self.dataBuff_uV = np.roll(self.dataBuff_uV, -1, axis=0)
                self.dataBuff_uV[-1] = sample.channel_data
                
                #dataBuffTemp = np.transpose(self.dataBuff_uV)
                
                dataBuff_filtered, zf = lfilter(self.b, self.a, self.dataBuff_uV, axis=0, zi=np.ones((8,16))*self.zi[:,None]*self.dataBuff_uV[0])
                self.dataBuff_filt_uV = lfilter(self.b2, self.a2, dataBuff_filtered, axis=0)
                self.plottr.inputBuff = self.dataBuff_filt_uV
                sample_string = "%s\n" % (str(np.std(np.transpose(self.dataBuff_filt_uV)[0])))
                #print "---------------------------------"
                #print sample_string
                #print "---------------------------------"        

        # DEBBUGING
        # try:
        #     sample_string.decode('ascii')
        # except UnicodeDecodeError:
        #     print "Not a ascii-encoded unicode string"
        # else:
        #     print sample_string

