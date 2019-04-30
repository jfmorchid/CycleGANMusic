'''
Main program
Function: to transfer the style of midi music
Steps:Predicting(with trained models),Strengthen(with music theory)
'''

from keras.models import load_model
import numpy as np
from music_theory import Main_Process
from midi_player import Export_Midi
import deal_with_midi
import sys


def Predicting(Musician, OriginalTrack):
    model = load_model("Models\\%s.hdf5" % (Musician))
    Input = OriginalTrack.reshape(1, 900, 1)  # the shape of input data: 1 sample * 900 dimension * 1 filter
    Output = model.predict(Input)
    Start, Duration = Output[3][0][:300], Output[3][0][600:]
    Start, Duration = [x[0] for x in Start], [x[0] for x in Duration]
    New_track = np.concatenate([Start, OriginalTrack[300:600], Duration])  # Ignore the note data of model output
    return New_track


if __name__ == '__main__':
    vector, style = sys.argv[1], sys.argv[2]
    try:
        print('Data preprocessing...')
        Track = np.array(deal_with_midi.Main_Process(vector, Type=2))  # preprocessing data
    except:
        raise RuntimeError('Invalid midi format. If it happens, you can contact us,and show us the invalid midi file.')
    Entire_track = [[0, '0', 0] for _ in range(len(Track) * 300)]
    try:
        print('Predicting with CycleGAN model...\n')
        for x in range(len(Track)):
            New_track = Predicting(style, Track[x])
            New_track, Lefthand_track = Main_Process(style, Track[x], New_track)
            Entire_track[x * 300:x * 300 + 300] = New_track
            print('Finishing parts %d / %d' % (x + 1, len(Track)))
    except:
        raise RuntimeError('Invalid discrete sequence. Please check the .mid format, and choose the suitable function to export sequence.')
    try:
        print('Saving to Output.mid...')
        Export_Midi('Output.mid', Entire_track)
    except:
        raise RuntimeError('Fail to save the midi file. Pleast make sure the Output.mid is not opened by other software.')
    print('Success!')
