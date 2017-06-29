import plugin_interface as plugintypes
import numpy as np
from scipy.signal import lfilter, butter

def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    cutoff = [lowcut / nyq, highcut / nyq]
    b, a = butter(order, cutoff, btype="bandpass")
    return b, a	

class PluginPrint(plugintypes.IPluginExtended):
    def __init__(self):
        self.dataBuffY_uV = np.zeros((16,32))
        self.yLittleBuff_uV = []
        self.dataBuffY_filtY_uV = np.empty((16,32))
        fs = 125
        order = 4
        lowcut = 1
        highcut = 50
        nyq = 0.5 * fs
        cutoff = [lowcut / nyq, highcut / nyq]
        self.b, self.a = butter(order, cutoff, btype="bandpass")
        self.b, self.a = butter_bandpass(lowcut, highcut, fs, order)



    def activate(self):
        print "Print activated"

    def filterIIR(self, filt_b, filt_a, data):
        Nback = len(filt_b)
        prev_y = []
        prev_x = [] 
        for i in range (0, len(data)):
            for j in range (Nback-1, 0):
                prev_y[j] = prev_y[j - 1]
                prev_x[j] = prev_x[j - 1]
        prev_x[0] = data[i]
        out = 0
        for j in range(0, Nback):
            out += filt_b[j] * prev_x[j]
            if (j > 0):
                out -= filt_a[j] * prev_y[j]
        prev_y[0] = out
        data[i] = out

    # called with each new sample
    def __call__(self, sample):
        if sample:
            #dataBuffLen = len(self.dataBuffY_uV)
            #sampleLen = len(sample.channel_data)

            #b = [
                #2.001387256580675e-001, 0.0, -4.002774513161350e-001, 0.0, 2.001387256580675e-001]
            #a = [1.0, -2.355934631131582e+000, 1.941257088655214e+000, -7.847063755334187e-001, 1.999076052968340e-001]

            #for i in range (0, sampleLen):
                #self.dataBuffY_uV[i] = np.roll(self.dataBuffY_uV[i], -1)
                #self.dataBuffY_uV[i][-1] = sample.channel_data[i]
                #self.dataBuffY_filtY_uV[i] = lfilter(self.b, self.a, self.dataBuffY_uV[i])

            sample_string = "ID: %f\n%s\n%s" %(sample.id, str(self.dataBuffY_filtY_uV[0])[1:-1], str(sample.aux_data)[1:-1])
            print "---------------------------------"
            print sample_string
            print "---------------------------------"

        

        # DEBBUGING
        # try:
        #     sample_string.decode('ascii')
        # except UnicodeDecodeError:
        #     print "Not a ascii-encoded unicode string"
        # else:
        #     print sample_string

