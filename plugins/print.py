import plugin_interface as plugintypes
import timeit
import math
import numpy as np
from scipy.signal import lfilter, butter, lfilter_zi

import matplotlib.pyplot as plt
import matplotlib.animation as animation

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

class PluginPrint(plugintypes.IPluginExtended):
    def activate(self):
        buffSize = int(self.sample_rate*8)
        nrOfChannels = self.eeg_channels
        self.dataBuff_uV = np.zeros((buffSize, nrOfChannels))
        self.dataBuff_filt_uV = np.zeros((buffSize, nrOfChannels))
        fs = self.sample_rate
        order = 4
        lowcut = 1
        highcut = 50
        self.b, self.a = butter_bandpass(lowcut, highcut, fs, order)
        #self.zi = lfilter_zi(self.b, self.a)

        self.b2, self.a2 = butter_bandstop(49, 51, fs, order)  # 50Hz
        fig, axes = plt.subplots(nrOfChannels, 1)

        lines = []

        for i in range(0, len(axes)):
            axes[i].set_ylim([-2000, 2000])
            lines.append(axes[i].plot(np.transpose(self.dataBuff_filt_uV)[i]))

        lines = np.squeeze(lines)
        plt.ion()

        def animate(i):
            for k in range(0, len(axes)):
                lines[k].set_ydata(np.transpose(self.dataBuff_filt_uV)[k])
            return [line for line in lines]

        ani = animation.FuncAnimation(fig, animate, np.arange(0, 128),
                                      interval=25, blit=True)
        plt.show()
        
        self.start_time = timeit.default_timer()
        self.openBCI_series_resistor_ohms = 2200
        self.leadOffDrive_amps = 6.0e-9
        print "Print activated"

    # called with each new sample
    def __call__(self, sample):
        if sample:
            self.dataBuff_uV = np.roll(self.dataBuff_uV, -1, axis=0)
            self.dataBuff_uV[-1] = sample.channel_data
            dataBuff_filtered = lfilter(self.b, self.a, self.dataBuff_uV, axis=0)
            #dataBuff_filtered, zf = lfilter(self.b, self.a, self.dataBuff_uV, axis=0,
                                            #zi=np.ones((len(self.zi), self.eeg_channels)) * self.zi[:, None] * self.dataBuff_uV[0])
            self.dataBuff_filt_uV = lfilter(self.b2, self.a2, dataBuff_filtered, axis=0)
            t = timeit.default_timer()
            if (t - self.start_time) >= 1:
                self.start_time = t
                print("---------------------------------")
                
                if sample.imp_data:
                    print("ID: " + str(sample.id))
                    for i in range(len(sample.channel_data)):
                        impTemp = sample.imp_data[i] / 1000
                        sample_string = "Ch %d: %.2f uV %.2f kOhm" %(i + 1, sample.channel_data[i], impTemp)
                        if impTemp > 30.0:
                            sample_string += " check electrode connection!"
                        print (sample_string)
                else:
                    sample_string = "ID: %f\n%s\n%s" %(sample.id, str(sample.channel_data)[1:-1], str(sample.aux_data)[1:-1])
                    print (sample_string)
                
                print("---------------------------------")

            # DEBBUGING
            # try:
            #     sample_string.decode('ascii')
            # except UnicodeDecodeError:
            #     print("Not a ascii-encoded unicode string")
            # else:
            #     print(sample_string)
