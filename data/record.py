import numpy as np
from tool.config import Config,LineConfig
from tool.qmath import normalize
from tool.dataSplit import DataSplit
import os.path
from re import split
from collections import defaultdict
class Record(object):
    'data access control'
    def __init__(self,config,trainingSet,testSet):
        self.config = config
        self.recordConfig = LineConfig(config['record.setup'])
        self.evalConfig = LineConfig(config['evaluation.setup'])
        self.name2id = defaultdict(dict)
        self.id2name = defaultdict(dict)
        self.artistListened = defaultdict(dict) #key:aritst id, value:{user id1:count, user id2:count, ...}
        self.albumListened = defaultdict(dict) #key:album id, value:{user id1:count, user id2:count, ...}
        self.trackListened = defaultdict(dict) #key:track id, value:{user id1:count, user id2:count, ...}
        self.artist2Album = defaultdict(dict) #key:artist id, value:{album id1:1, album id2:1 ...}
        self.album2Track = defaultdict(dict) #
        self.artist2Track = defaultdict(dict) #
        self.userRecord = defaultdict(list) #user data in training set. form: {user:[record1,record2]}
        self.testSet = defaultdict(dict) #user data in test set. form: {user:{recommenedObject1:1,recommendedObject:1}}
        self.recordCount = 0
        if self.evalConfig.contains('-byTime'):
            trainingSet,testSet = self.splitDataByTime(trainingSet)
        self.preprocess(trainingSet,testSet)

    def splitDataByTime(self,dataset):
        trainingSet = []
        testSet = []
        ratio = float(self.evalConfig['-byTime'])
        records = defaultdict(list)
        for event in dataset:
            records[event['user']].append(event)
        for user in records:
            orderedList = sorted(records[user],key=lambda d:d['time'])
            training = orderedList[0:int(len(orderedList)*(1-ratio))]
            test = orderedList[int(len(orderedList)*(1-ratio)):]
            trainingSet += training
            testSet += test
        return trainingSet,testSet


    def preprocess(self,trainingSet,testSet):
        for entry in trainingSet:
            self.recordCount+=1
            for key in entry:
                if key!='time':
                    if not self.name2id[key].has_key(entry[key]):
                        self.name2id[key][entry[key]] = len(self.name2id[key])
                        self.id2name[key][len(self.id2name[key])] = entry[key]

                if key=='user':
                    self.userRecord[entry['user']].append(entry)
                    if entry.has_key('artist'):
                        if not self.artistListened[entry['artist']].has_key(entry[key]):
                            self.artistListened[entry['artist']][entry[key]] = 0
                        else:
                            self.artistListened[entry['artist']][entry[key]] += 1
                    if  entry.has_key('album'):
                        if not self.albumListened[entry['album']].has_key(entry[key]):
                            self.albumListened[entry['album']][entry[key]] = 0
                        else:
                            self.albumListened[entry['album']][entry[key]] += 1
                    if entry.has_key('track'):
                        if not self.trackListened[entry['track']].has_key(entry[key]):
                            self.trackListened[entry['track']][entry[key]] = 0
                        else:
                            self.trackListened[entry['track']][entry[key]] += 1
                if key == 'artist' and entry.has_key('album'):
                        self.artist2Track[entry[key]][entry['album']] = 1
                if key == 'album' and entry.has_key('track'):
                        self.album2Track[entry[key]][entry['track']] = 1
                if key == 'artist' and entry.has_key('track'):
                    self.artist2Track[entry[key]][entry['artist']] = 1


        recType = self.evalConfig['-target']
        for entry in testSet:
            for key in entry:
                if key != 'time':
                    if not self.name2id[key].has_key(entry[key]):
                        self.name2id[key][entry[key]] = len(self.name2id[key])
                        self.id2name[key][len(self.id2name[key])] = entry[key]
                if key=='user':
                    if entry.has_key(recType):
                        self.testSet[entry['user']][entry[recType]]=1


    def printTrainingSize(self):
        if self.name2id.has_key('user'):
            print 'user count:',len(self.name2id['user'])
        if self.name2id.has_key('artist'):
            print 'artist count:',len(self.name2id['artist'])
        if self.name2id.has_key('album'):
            print 'album count:',len(self.name2id['album'])
        if self.name2id.has_key('track'):
            print 'track count:', len(self.name2id['track'])
        print 'Training set size:',self.recordCount


    def getId(self,obj,t):
        if self.name2id[t].has_key(obj):
            return self.name2id[t][obj]
        else:
            print 'No '+t+' '+obj+' exists!'
            exit(-1)

    def getSize(self,t):
        return len(self.name2id[t])



