'''
Main program
Function: to transfer the style of midi music
Steps:Predicting(with trained models),Strengthen(with music theory)
'''

from keras.models import load_model
import numpy as np
from music_theory import Main_Process
from midi_player import Export_Midi
import sys


def Predicting(Musician, OriginalTrack):
    model = load_model("Models\\%s.hdf5" % (Musician))
    Input = OriginalTrack.reshape(1, 900, 1)  # the shape of input data: 1 sample * 900 dimension * 1 filter
    Output = model.predict(Input)
    Start, Duration = Output[3][0][:300], Output[3][0][600:]
    Start, Duration = [x[0] for x in Start], [x[0] for x in Duration]
    New_track = np.concatenate([Start, OriginalTrack[300:600], Duration])  # Ignore the note data of model output
    return New_track


vector, style = sys.argv[1], sys.argv[2]
f = open(vector)
Track = f.readlines()
f.close()
Track = [int(x) for x in Track[0][:-1].split(' ')]
Track = np.array(Track)
New_track = Predicting(style, Track)
New_track, Lefthand_track = Main_Process(style, Track, New_track)
Export_Midi('Output.mid', New_track)
