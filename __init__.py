'''
Main program
Function: to transfer the style of midi music
Steps:Predicting(with trained models),Strengthen(with music theory)
'''

from keras.models import load_model
import numpy as np
from music_theory import Main_Process
from midi_player import Export_Midi

def Predicting(Musician,OriginalTrack):
    model=load_model("Models\\%s.hdf5"%(Musician))
    Input=OriginalTrack.reshape(1,900,1)    #the shape of input data: 1 sample * 900 dimension * 1 filter
    Output=model.predict(Input)
    Start,Duration=Output[3][0][:300],Output[3][0][600:]
    Start,Duration=[x[0] for x in Start],[x[0] for x in Duration]
    New_track=np.concatenate([Start,OriginalTrack[300:600],Duration])   #Ignore the note data of model output
    return New_track

f=open("data\\TrainingData\\V.K\\V.K.Sample0.txt")
Track=f.readlines()
f.close()
Track=[int(x) for x in Track[0][:-1].split(' ')]
Track=np.array(Track)
New_track=Predicting('Beethoven',Track)
New_track,Lefthand_track=Main_Process('Beethoven',Track,New_track)
Export_Midi('Beethoven.mid',New_track)