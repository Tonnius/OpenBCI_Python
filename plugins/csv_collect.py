import csv
import timeit
import datetime
import random
import plugin_interface as plugintypes
import os

INITIAL_PAUSE_LENGTH = 6 #should be about 6
TRAINING_LENGTH = 4
EXTRA_RECORDING_TIME = 0
RECORDING_LENGTH = TRAINING_LENGTH + EXTRA_RECORDING_TIME
RANDOM_PAUSE_MIN = 4 - EXTRA_RECORDING_TIME #must be positive
RANDOM_PAUSE_MAX = RANDOM_PAUSE_MIN + 4 #must be positive

trainingDirections = [1,2,3,4] * 5 #1 - left (hand), 2 - right (hand), 3 - up (tongue), 4 - down (right foot), 0 - base (no action)

def print_arrow():
    if not trainingDirections:
        #globalVars.trainingDone = True
        print 'Training ended'
        exit()
        return -1
    else:
        direct = trainingDirections.pop()
        if(direct == 1):    
            print '    <|\n  <<<|======\n<<<<<|left==\n  <<<|======\n    <|'
        elif(direct == 2):
            print '      |>    \n======|>>>  \n=right|>>>>>\n======|>>>  \n      |>    '
        elif(direct == 3):
            print '     ^^   \n    ^^^^  \n   ^ up ^ \n  ^^^^^^^^\n    ||||   '
        elif(direct == 4):
            print '    ||||  \n  vvvvvvvv\n   vdownv \n    vvvv  \n     vv   '
        else:
            print 'Unknown direction in training array'
            return -1
        return direct
    
class PluginCSVCollect(plugintypes.IPluginExtended):
    def __init__(self, file_name="collect.csv", delim = ",", verbose=False):
        now = datetime.datetime.now()
        self.timeStamp = '%d-%d-%d_%d-%d-%d'%(now.year,now.month,now.day,now.hour,now.minute,now.second)
        self.fileNameData = self.timeStamp
        self.fileNameEvents = self.timeStamp
        self.startTime = 0
        self.delim = delim
        self.verbose = verbose
        self.trainingStart = 0
        self.pauseStart = 0
        random.shuffle(trainingDirections)
        self.directionToFile = 0
        self.randomPauseInSec = 0
        self.directionStop = 0
        
    def activate(self):
        if len(self.args) > 0:
            if 'no_time' in self.args:
                self.fileNameData = self.args[0]
                self.fileNameEvents = self.args[0]
            else:
                self.fileNameData = self.args[0] + '_' + self.fileNameData;
                self.fileNameEvents = self.args[0] + '_' + self.fileNameEvents;
            if 'verbose' in self.args:
                self.verbose = True

        self.fileNameData = self.fileNameData + '_data.csv'
        self.fileNameEvents = self.fileNameEvents + '_events.csv'
        print "Will export CSV to:", self.fileNameData
        
        dataHeader = self.timeStamp
        for i in range (16): #replace with EEG channels count
            dataHeader += self.delim
            dataHeader += str(i)
        
        eventsHeader = self.timeStamp+self.delim+'left'+self.delim+'right'+self.delim+'up'+self.delim+'down'
        
        #Open in append mode
        with open(self.fileNameData, 'a') as f:
            f.write(dataHeader + '\n')
            
        with open(self.fileNameEvents, 'a') as g:
            g.write(eventsHeader + '\n')
            
    def deactivate(self):
        print "Closing, CSV saved to:", self.fileNameData
        return

    def show_help(self):
        print "Optional argument: [filename] (default: collect.csv)"

    def __call__(self, sample):
        if sample and len(sample.channel_data) == 16:
            if (self.startTime == 0):
                self.startTime = timeit.default_timer()
                print 'Initial pause start'

            t = timeit.default_timer() - self.startTime
            

            if(t >= INITIAL_PAUSE_LENGTH and self.trainingStart == 0):
                self.trainingStart = t
                print 'Initial pause end'
                         
            if(t - self.trainingStart >= self.randomPauseInSec + RECORDING_LENGTH and self.trainingStart != 0):
                #print(chr(27) + "[2J")
                os.system('cls' if os.name == 'nt' else 'clear')
                self.directionStop = self.pauseStart = self.trainingStart = t
                self.randomPauseInSec = random.uniform(RANDOM_PAUSE_MIN, RANDOM_PAUSE_MAX)
                print '------------------\n'
                self.directionToFile = print_arrow()
                print '\n------------------'
            
            if(t - self.pauseStart >= TRAINING_LENGTH and self.pauseStart != 0):  
                self.pauseStart = 0
                os.system('cls' if os.name == 'nt' else 'clear')
                print '------------------\n'
                print '     |\n     |\n-----X-----\n     |\n     |'
                print '\n------------------'
                print '\nPause '# + str(self.randomPauseInSec) + ' sec'
                
            if(t - self.directionStop >= RECORDING_LENGTH and self.directionStop != 0):  
                self.directionStop = 0
                self.directionToFile = 0
            
            #print timeSinceStart|Sample Id
            if self.verbose:
                print("CSV: %f | %d" %(t,sample.id))

            row = ''
            row += str(t)
            #row += self.delim
            #row += str(sample.id)
            #row += self.delim
            for i in sample.channel_data:
                row += self.delim
                row += str(i)
                
            
            #for i in sample.aux_data:
                #row += str(i)
                #row += self.delim
            
            row += '\n'
            with open(self.fileNameData, 'a') as f:
                f.write(row)
            
            row = ''
            row += str(t)
            row += self.delim
            if(self.directionToFile == 1):
                row += '1' + self.delim + '0' + self.delim + '0' + self.delim + '0'
            elif(self.directionToFile == 2):
                row += '0' + self.delim + '1' + self.delim + '0' + self.delim + '0'
            elif(self.directionToFile == 3):
                row += '0' + self.delim + '0' + self.delim + '1' + self.delim + '0'
            elif(self.directionToFile == 4):
                row += '0' + self.delim + '0' + self.delim + '0' + self.delim + '1'
            else:
                row += '0' + self.delim + '0' + self.delim + '0' + self.delim + '0'
                
            row += '\n'
            with open(self.fileNameEvents, 'a') as g:
                g.write(row)