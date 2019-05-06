'''
Module Name=music_theory
Function: to optimize the music with music theory
Remark: Optimization steps:
        1.expand absolute difference
        2.Speed  configuration
        3.Length regularization
        4.Add chord
        5.add left-hand_Melody (another midi track)
'''

import numpy as np
from mido import MidiTrack,Message
from midi_player import Initialize_Track
unit={"V.K":81,"Hisaishi":129,"Debussy":66,"Pianoboy":152,"Beethoven":36,"Bach":68,"Mozart":75,"Schubert":38}#unit length of note
speed={"V.K":0.76,"Hisaishi":1,"Debussy":1,"Pianoboy":1,"Beethoven":1,"Bach":1,"Mozart":1,"Schubert":1}
ratio={"V.K":1.1,"Hisaishi":1,"Debussy":1,"Pianoboy":1,"Beethoven":1,"Bach":1,"Mozart":1,"Schubert":1}
'''
Function name:Expand_Absolute
Task: to amplify the results of neural network training
Input:two numpy arrays (Original,New), ratio of expansion (a hyperparameter,measured by variance)
Output:another numpy array (absolute difference expanded)
'''
def Expand_Absolute(Original,New,ratio=1):
    Expanded=New+ratio*(New-Original)
    return((Expanded+abs(Expanded))/2) # change all negative element into zero

'''
Function name:Speed_Configuration
Task: to configure the speed of music
Input: a numpy array , musician
output: another numpy array(speed configured)
Remark: We measure the speed of music by time spend of these notes.
'''

def Speed_Configuration(Track,Musician):
    ratio=speed[Musician]            #the ratio of zoom
    for x in range(300):
        Track[x]*=ratio
        Track[x+600]*=ratio
    return Track

'''
Function name:Length_Regularization
Task: to adjust the tempo according to musician's personal habit without breaking the structure of CycleGAN output
Input: numpy array of music, musician, upper bound, lower bound
Output:another numpy array (length of note regularized), lists of start & end notes of each section,list of beginning position of each section
Remark: the adjusting process is essential so that we can use chord accompaniment technique to promote the quality of music
        Without stable tempo,the music with accompaniment will not be fascinating at all.
        To avoid abnormal rhythm, we just keep notes with the duration from lower bound to upper bound 
        upper bound is always set to be 4*unit while lower bound is set to be unit
'''
def Length_Regularization(Track,Musician,lower=20,upper=900):
    
    '''
    Sub function:Rearrange_Section
    Task:to rearrange notes into standard sections
    Input:a list of note in one section (including 3 parameters in each sample:start,note,duration) ,musician, remaining interval
    Output:a list of rearranged note , and remaining interval of next section ,start note of the section, end note of the section
    Remark: we use start note of section to decide which type of chord, and use end note to decide left hand melody
    '''
    def Rearrange_Section(L,Musician,Remain):
        for x in range(len(L)):
            if(L[x][2]==3*unit[Musician]):      #we only allow 1,2,4,6,8 units as duration of note
                L[x][2]=2*unit[Musician]
            elif(L[x][2]==5*unit[Musician]):
                L[x][2]=4*unit[Musician]
            elif(L[x][2]==7*unit[Musician]):
                L[x][2]=6*unit[Musician]
            elif(L[x][2]>=9*unit[Musician]):
                L[x][2]=8*unit[Musician]
        Occupied=[False for _ in range(8)]  #whether the position in this section is occupied
        pos=0  #current position
        L[0][0]=Remain  #the start of section
        for x in range(pos):
            Occupied[x]=True
        for x in range(1,len(L)):
            pos+=int(L[x][0]//unit[Musician])
            if(pos%2==1):
                if(not(Occupied[pos-1])):       #invalid appearance on half-tone position
                    pos-=1
                    L[x][0]-=unit[Musician]
                    for i in range(pos,pos+int(L[x][2]//unit[Musician])):
                        Occupied[i]=True        #the position is occupied by this note                    
                elif(int((L[x][2]//unit[Musician]))%2==0):  #invalid duration of note on half-tone position,cut it off!
                    L[x][2]-=unit[Musician]
                    if(pos+int(L[x][2]//unit[Musician])>8):
                        L[x][2]-=unit[Musician]*(pos+int(L[x][2]//unit[Musician])-8)    #cut off long note
                    for i in range(pos,pos+int(L[x][2]//unit[Musician])):
                        Occupied[i]=True
            else:
                if(pos+int(L[x][2]//unit[Musician])>8):
                    L[x][2]-=unit[Musician]*(pos+int(L[x][2]//unit[Musician])-8)    #cut off long note
                for i in range(pos,pos+int(L[x][2]//unit[Musician])):
                    Occupied[i]=True
            pos+=int(L[x][2]//unit[Musician])
        Next_remain=int(unit[Musician]*(8-pos))
        return L,Next_remain,L[0][1],L[-1][1]
    
    for x in range(300):
        if(Track[600+x]<lower):    #stretch this short note 
            Track[600+x]=lower
        elif(Track[600+x]>upper):   #cut off this long note
            Times_of_unit=int(upper/unit[Musician]+0.5) #round the unit multiplication
            Track[600+x]=unit[Musician]*(Times_of_unit)   #limit it to upper bound
        else:                          #keep integer multiples of the unit
            Times_of_unit=int(Track[600+x]/unit[Musician]+0.5)
            Track[600+x]=unit[Musician]*(Times_of_unit)
        if(Track[x]<lower):    #stretch this short note 
            Track[x]=0
        elif(Track[x]>upper):   #cut off this long note
            Times_of_unit=int(upper/unit[Musician]+0.5)
            Track[x]=unit[Musician]*(Times_of_unit)   #limit it to upper bound
        else:                          #keep integer multiples of the unit
            Times_of_unit=int(Track[x]/unit[Musician]+0.5)
            Track[x]=unit[Musician]*(Times_of_unit)
    Track[0]=0
    
    pos,Remain,begin=0,0,0   #rearrange the section according to music theory
    Start_of_section,End_of_section,Begin_of_section=[],[],[]
    while(pos<300):
        Interval=0
        while(Interval<8*unit[Musician] and pos<300):
            Interval+=Track[pos+600]+Track[pos]
            pos+=1
        Section=[[Track[x],Track[x+300],Track[x+600]] for x in range(begin,pos-1)]
        Section,Remain,Start,End=Rearrange_Section(Section,Musician,Remain) #rearrangement
        Start_of_section.append(Start)
        End_of_section.append(End)
        Begin_of_section.append(begin)
        for x in range(len(Section)):
            Track[begin+x],Track[begin+x+300],Track[begin+x+600]=Section[x]
        begin=pos-1
    for x in range(900):
        if(Track[x]<0):
            Track[x]=0
    return Track,Start_of_section,End_of_section,Begin_of_section


'''
Function name:Add_Chord
Task: to add chord to the main rhythm
Input:a numpy array , musician , start note of each section, beginning position of each section
Output:a sequence list
'''
def Add_Chord(Track,Musician,Start,Begin):
    
    '''
    Sub function:Chord_Type
    Task:to add a chord according to the particular type
    Input:a note (the root) , type of chord( M , m , M7 , m7 , dim , aug)
    Output:a list of note arranged according to chord theorem
    '''
    def Chord_Type(root,Type='M'):
        if(Type=='M'):  #major triad
            return [root,root+4,root+7] 
        elif(Type=='m'):   #minor triad
            return [root,root+3,root+7]
        elif(Type=='M7'):    #major seventh chord
            return [root,root+4,root+7,root+11]
        elif(Type=='m7'):    #minor seventh chord
            return [root,root+3,root+7,root+10]
        elif(Type=='dim'):  #dimished triad
            return [root,root+3,root+6,root+9]
        elif(Tyie=='aug'):
            return [root,root+4,root+8]
    Sequence=[[] for _ in range(300)]
    for x in range(300):
        if(x in Begin):
            Type='M'
            if(Begin.index(x)==0):
                Type='M7'
            elif(Start[Begin.index(x)] in [60,64,67,48,51,55,72,76,79,84,88,91]):   #do mi so
                Type='M'
            else:
                Type='m'
            Sequence[x]=[Track[x],Chord_Type(Track[300+x],Type),Track[x+600]]    #attach a chord to the note
            Sum=0
        else:
            Sequence[x]=[Track[x],[Track[300+x]],Track[x+600]]
    return Sequence

'''
Function name:Lefthand_Melody
Task: to add left-hand melody for each sections
Input:main melody,end note of each section , musician ,sections(1 represents 1 round each section, 2 means 1 round each 2 section,etc.)
Output: left-hand track
'''
def Lefthand_Melody(Main,End,Musician):
    
    '''
    Sub function : Append_Note
    Task: to append assistant notes
    Input: Track , note list , start(gap between 2 assistant notes),musician
    Output:Track
    '''
    def Append_Note(Track,L,start,Musician):
        for x in L:
            if(L.index(x)==0):
                Track.append(Message('note_on',channel=0,note=x,velocity=64,time=int(start)))
                Track.append(Message('note_off',channel=0,note=x,velocity=64,time=1*unit[Musician]))
            else:
                Track.append(Message('note_on',channel=0,note=x,velocity=64,time=1*unit[Musician]))
                Track.append(Message('note_off',channel=0,note=x,velocity=64,time=1*unit[Musician]))
        return Track

    Track=Initialize_Track()
    Time=Main[0][0]+Main[0][2]  #absolute time axis
    Last_place=0
    for x in range(1,len(Main)):
        if(((Time+Main[x][0])//unit[Musician])%2==0 and ((Time-Main[x-1][2])//unit[Musician])%2==0 and ((Main[x-1][2]+Main[x][0])//unit[Musician])%4==0): #need assistant notes
            start=Time-Last_place+2*unit[Musician]   #gap between two assistant notes
            Last_place=Time+Main[x][0]+Main[x][2]
            if(Main[x-1][2]+Main[x][0] == 16*unit[Musician]):    #there are 7 units between 2 notes: do 0 * 0 mi 0 do
                Track=Append_Note(Track,[48,0,48+int(Main[x-1][1][0]-5)%12,0,52,0,48],start,Musician)
            elif(Main[x-1][2]+Main[x][0] == 12*unit[Musician]):  #there are 5 units between 2 notes: do 0 * 0 do
                Track=Append_Note(Track,[48,0,48+int(Main[x-1][1][0]-5)%12,0,48],start,Musician)
            elif(Main[x-1][2]+Main[x][0] == 8*unit[Musician]):  #there are 3 units between 2 notes: void * void
                Track=Append_Note(Track,[0,48+int(Main[x-1][1][0]-5)%12,0],start,Musician)
            elif(Main[x-1][2]+Main[x][0] == 6*unit[Musician]):  #there are 1 units between 2 notes: * do
                Track=Append_Note(Track,[48+int(Main[x-1][1][0]-5)%12,48],start,Musician)           
            elif(Main[x-1][2]+Main[x][0] == 4*unit[Musician]):  #there are 1 units between 2 notes: *
                Track=Append_Note(Track,[48+int(Main[x-1][1][0]-5)%12],start,Musician) 
        Time+=Main[x][0]+Main[x][2]
    return Track
'''
Function name:Main_Process
Task: to execute the entire procedure of optimization
Input:musician, original track, new track
Output: the final result of optimization (main track and left-hand track)
'''
def Main_Process(Musician,Original,New):
    Track=Speed_Configuration(New, Musician)#step1
    Track=Expand_Absolute(Original,Track,ratio[Musician])   #step2
    Track,Start,End,Begin=Length_Regularization(Track,Musician,lower=unit[Musician],upper=unit[Musician]*4) #step3
    Track=Add_Chord(Track,Musician,Start,Begin) #step4
    Left_track=Lefthand_Melody(Track,End, Musician)    #step5
    return Track,Left_track

