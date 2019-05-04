'''
Model Name:infer_with_browser
Function: handle the inferenced data from cycleGAN in .json format
'''

import json
from midi_player import Export_Midi,Note_Split
import numpy as np
from music_theory import Main_Process
import deal_with_midi
import sys

'''
Function name:Decode_Json
Task: to decode json data uploaded from cycleGAN
Input: data with json format
Output: the list which can be operated by other function
'''


def Decode_Json(data):

    Track, Original, style = data['Array'], np.array(data['Original']), data['Style']
    Entire_track = [[0, '0', 0] for _ in range(len(Track) * 300)]
    for x in range(len(Track)):
        Sub_track = np.array([L[0] for L in Track[x]])
        New_track = np.concatenate([Sub_track[:300], Original[x][300:600], Sub_track[600:]])
        New_track, Lefthand_track = Main_Process(style, Original[x], New_track)
        Entire_track[x * 300:x * 300 + 300] = New_track
    return Entire_track


if __name__ == '__main__':
    f = open("sequence.json")
    data = json.load(f)
    Track = Decode_Json(data)
    #Export_Midi('Output.mid', Track)
    Note_Split(Track)
