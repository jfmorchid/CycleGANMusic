'''
Module Name: midi_player
Function: to play a music -- save the .mid file written according to discrete sequence
'''

import deal_with_midi
from mido import MidiTrack,MidiFile,Message,MetaMessage
import os

'''
Function name: Initialize_Track
Task: to initialize the track in aspects of instrument,tempo and key signature
Input: instrument (int) , tempo (int) ,key (char from 'A' to 'F')
Output: the initialized midi track
Default: instrument=1 (piano) , tempo=714280(default) , key='C'
'''
def Initialize_Track(Instrument=1,Tempo=714280,Key='C'):
    Track=MidiTrack()
    Track.append(MetaMessage("track_name",name='Musicine',time=0))
    Track.append(MetaMessage('key_signature',key=Key,time=0))
    Track.append(Message('program_change',channel=0,program=Instrument,time=0)) #change the type of instrument
    Track.append(MetaMessage("set_tempo",tempo=Tempo,time=0))
    return Track

'''
Function name:Add_Notes
Task: to add notes from discrete sequence
Input: initialized Track , path of midi (or sequence) ,type (sequence or midi, default midi) , ratio(slow down || speed up ,default 1x)
Output: the midi file
Remark: the list "Command" includes 3 parts:
        Command[0] : start time (Relative)
        Command[1] : list of notes
        Command[2] : duration time
'''
def Add_Notes(Track,path,Type='midi',ratio=1):
    if(Type=='midi'):       #deal with midi
        Sequence=deal_with_midi.Main_Process(path)
    else:   #deal with discrete sequence
        Sequence=path  #generating operation list

    for Command in Sequence:
        Track.append(Message('note_on',channel=0,note=int(Command[1][0]),velocity=90,time=int(Command[0])))   #Main note
        for Notes in range(1,len(Command[1])):  #Assistant note
            Track.append(Message('note_on',channel=0,note=int(Command[1][Notes]),velocity=48,time=0))     
        Track.append(Message('note_off',channel=0,note=int(Command[1][0]),velocity=90,time=int(Command[2])))  #Main note ends
        for Notes in range(1,len(Command[1])):  #Assistant note ends
            Track.append(Message('note_off',channel=0,note=int(Command[1][Notes]),velocity=48,time=0))          
    Music=MidiFile()
    Music.tracks.append(Track)
    return Music

'''
Function name:Batch_Export
Task:to export all sequence from a particular musician at the same time
Input:Name of the musician (Use Beethoven's format only)
Output:None
'''
def Batch_Export(Musician):
    Path_list=os.listdir("data\\Midi\\%s"%(Musician))
    for x in Path_list:
        path="data\\Midi\\%s\\%s"%(Musician,x)
        Track=Initialize_Track()
        Music=Add_Notes(Track,path)

'''
Function name:Export_Midi
Task:to export the music into .mid file
Input:Name of midi, sequence of midi, left hand track(if exists)
Output:None
'''
def Export_Midi(Name,Sequence,Lefthand=None):
    Track=Initialize_Track()
    Music=Add_Notes(Track,Sequence,'sequence')
    if(not(Lefthand==None)):        #left-hand melody
        Music.tracks.append(Lefthand)
    Music.save(Name)    
#Batch_Export("Schubert") #this is a preprocessing part

