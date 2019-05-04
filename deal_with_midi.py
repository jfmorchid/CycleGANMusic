'''
Module Name:deal_with_midi
Function: convert midi into discrete note sequence
'''

from mido import MidiFile, MidiTrack, Message
import midi_player


'''
Function Name:Format_Convert
Task: to convert the format of another type of midi (from http://www.piano-midi.de/)
Input: the path of midi file
Output:a list of string including all commands in a unified format
Remark: this type of midi data has 2 track:
        track 0 : set tempo
        track 1 : seet notes
We don't want to set tempo frequently,so we adjust the time according to the tempo
'''


def Format_Convert(path):
    Song = MidiFile(path)  # load the midi file
    for i, track in enumerate(Song.tracks):
        if(i == 0):
            Tempo_track = track  # the track with meta message "set_tempo"
        elif(i == 1):
            Note_track = track  # the track with message "note_on"
    Start, Each_tempo, Time_lag = [], [], 0  # record points where tempo is changed
    for x in Tempo_track:
        Command = str(x).split(' ')
        if(not(Command[-2][:6] == 'tempo=')):  # not the set_tempo message
            Time_lag += int(Command[-1][5:-1])  # they occupy timeline as well
        else:
            Start.append(Time_lag + int(Command[-1][5:-1])), Each_tempo.append(int(Command[-2][6:]))
            Time_lag = 0

    Tempo_index, Time_wentby = 0, 0  # to calculate the tempo interval
    Note_track = [x for x in Note_track if "_on" in str(x)]
    Onoff_track = Note_track
    for x in range(len(Note_track)):
        Command = str(Note_track[x]).split(' ')
        Time_wentby += int(Command[-1][5:])
        while(Time_wentby >= Each_tempo[Tempo_index]):
            Time_wentby -= Each_tempo[Tempo_index]
            Tempo_index += 1  # calculate which tempo it is at present
        Ratio = Each_tempo[Tempo_index] / 714280  # zoom ratio
        if(Command[-2] == 'velocity=0'):  # it's equivalent to message "note_off"
            Onoff_track[x] = "note_off channel=0 note=%s velocity=64 time=%d" % (Command[2][5:], int(int(Command[-1][5:]) * Ratio))
        else:  # it's equivalent to message "note_on"
            if(int(Command[2][5:])<60): #assistant note
                Onoff_track[x] = "note_on channel=0 note=%s velocity=64 time=%d" % (Command[2][5:], int(int(Command[-1][5:]) * Ratio))
            else:
                Onoff_track[x] = "note_on channel=0 note=%s velocity=90 time=%d" % (Command[2][5:], int(int(Command[-1][5:]) * Ratio))

    return Onoff_track


'''
Function name:Export_Midi
Task: to export midi's commands
Input: the path of midi file
Output: a list of string including all commands
'''


def Export_Midi(path):
    Song = MidiFile(path)  # load the midi file
    for i, track in enumerate(Song.tracks):
        if(i == 1):
            Main_track = track  # the main track of midi music
    Onoff_track = [str(x) for x in Main_track]
    return Onoff_track


'''
Function name:Discrete_Sequence
Task: to convert the midi commands to discrete sequence
Input: a list of string including all commands , ratio(speed up || slow down , default 1)
Output: a list of discrete notes
Remark: the discrete sequence has a unified format:
        Starting time(Relative)  Note1,Note2,...  Duration time
        the "on" command and "off" command is matched, which means that we merely need to notice on "on" command 
'''


def Discrete_Sequence(Track, ratio=1):
    Start_time, Duration_time, Change_time = 0, 0, 0  # "control change" command makes a time lag
    Sequence = []  # 3 parameters:start time, notes, duration time
    Note_list = []    # a list of note playing at the same time
    for x in range(len(Track)):
        if "_on" in Track[x]:  # "note_on" command
            Command = Track[x].split(' ')
            if(not(x == 0) and ("_on" in Track[x - 1])):  # Assistant note
                Note_list.append(Command[2][5:])  # add the note into list
                Change_time += int(int(Command[-1][5:]) * ratio)
            else:  # Main note
                Start_time = int(int(Command[-1][5:]) * ratio) + Change_time
                Change_time = 0
                Note_list = [Command[2][5:]]
        elif "_off" in Track[x]:  # "note_off" command
            Command = Track[x].split(' ')
            if(not(Command[-1] == 'time=0')):  # Main note ends
                Duration_time = int(int(Command[-1][5:]) * ratio) + Change_time
                Change_time = 0
                Sequence.append([Start_time, Note_list, Duration_time])
        else:
            Command = Track[x].split(' ')
            if(Command[-1][-1] == '>'):  # meta message:time=**>
                Command[-1] = Command[-1][:-1]
            if(not(Command[-1] == 'time=0')):  # the time lag exists
                Change_time += int(int(Command[-1][5:]) * ratio)
    return Sequence


'''
Function name:Export_Sequence
Task:to export the discrete sequence into a .txt file
Input: path of .mid file(it will be changed into .txt soon) , discrete sequence
Output:None
'''


def Export_Sequence(path, Sequence):
    Txt_path = path[:-3] + 'txt'
    Txt_path = Txt_path.replace('Midi', 'Sequence')
    f = open(Txt_path, 'w', encoding='utf-8')
    for x in Sequence:  # ignore assistant note while training
        f.write("%d %s %d\n" % (x[0], x[1][0], x[2]))
    f.close()

'''
Function name:Main_Process
Task: to convert the midi file (in YuHsin format) into sequence
Input:the path of midi file 
Output:the corresponding discrete sequence
'''

def YuHsin(path):
    Song = MidiFile(path)  # load the midi file
    for i, track in enumerate(Song.tracks):
        if(i == 0):
            Main_track = track  # the main track of midi music
    Onoff_track = [str(x) for x in Main_track]  
    Track=[]    #the target list
    Last_off=0 #the last duration time of note_off command
    for x in Onoff_track:
        command=x.split(' ')
        if('note_on' in x and command[-1][5:]!='0' and int(command[-2][9:])>=45):
            Track.append("note_on %s %s %s time=%d"%(command[1],command[2],command[3],Last_off))
            Track.append("note_off %s %s %s time=%d"%(command[1],command[2],command[3],int(command[-1][5:])))
            Last_off=0
        elif('note' in x and command[-1][5:]!='0'):
            Last_off+=int(command[-1][5:])   #record the note_off time
    return Track
'''
Function name:Main_Process
Task: the entire process to convert a midi file into discrete sequence
Input:the path of midi file , type of midi file (2 source,0 means Beethoven... , 1 means V.K...,defalt 2 -- common style in the software)
Output:the corresponding discrete sequence
'''


def Main_Process(path, Type=2):
    if(Type==0):  # use V.K format
        Track = Export_Midi(path)
    elif(Type==1):  # use Beethoven format
        Track = Format_Convert(path)
    elif(Type==2):  #use YuHsin format(default)
        Track = YuHsin(path)
    Sequence = Discrete_Sequence(Track)
    parts=(len(Sequence)-1)//300+1  #300 notes is regarded as 1 part
    for x in range(300*parts-len(Sequence)):
        Sequence.append([0,['0'],0])    #filled with empty note when the last part is less then 300 notes
    L=[[0 for _ in range(900)] for _ in range(parts)]
    for i in range(parts):
        Sub_sequence=Sequence[300*i:300*i+300]
        L[i][:300]=[x[0] for x in Sub_sequence]
        L[i][300:600]=[int(x[1][0]) for x in Sub_sequence]
        L[i][600:]=[x[2] for x in Sub_sequence]
    return L

if __name__=='__main__' :
    x=Main_Process("jipusai.mid",Type=2)
    print(x)