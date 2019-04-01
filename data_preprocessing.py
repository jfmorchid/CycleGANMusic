'''
Module Name:data_preprocessing
Function: to split these discrete sequences into several standard training data files
Remark: a stardard training data includes 300 notes(The missing data is populated with 0,0,0)
        Considering that the sample data is closely related to the timeline,We collect data every 100 notes.
'''

import os
from random import randint
import numpy as np

'''
Function name:Load_Sequence
Task: to load all discrete midi sequences of a particular musician
'''
def Load_Sequence(Musician):
    Path_list=os.listdir("data\\Sequence\\%s"%(Musician))
    order=0
    for x in Path_list:
        f=open("data\\Sequence\\%s\\%s"%(Musician,x))
        Sequence=f.readlines()
        Sequence=[L[:-1] for L in Sequence] #eliminate "\n"
        index=0     # head of the sampling interval
        while(len(Sequence)>index):
            One_input=['0' for _ in range(900)]
            Partof_Sequence=[i.split(' ') for i in Sequence[index:index+300]]      #a part of sequence including 300 notes
            for i in range(len(Partof_Sequence)):
                One_input[i],One_input[i+300],One_input[i+600]=Partof_Sequence[i][0],Partof_Sequence[i][1],Partof_Sequence[i][2]
            Random_Noise(One_input,Musician,order)
            index,order=index+100,order+3
        f.close()

'''
Function name: Random_Noise
Task: accomplish random data enhancement by introducing random noise,and then export them
Input:loaded sequence, musician , order of the training data
Output:None
'''
def Random_Noise(Sequence,Misician,order):
    f=open("data\\TrainingData\\%s\\%s.Sample%d.txt"%(Misician,Misician,order),'w')
    for notes in Sequence:
        f.write(notes+" ")
    f.close()
    for i in range(2):      #Enhance twice
        for x in range(len(Sequence)):
            probility=randint(0,100)
            if(probility<3):     # 3% to introduce random noise
                Sequence[x]=str(int(Sequence[x])-3+randint(0,6))
                if(int(Sequence[x])<0):   #time interval must be non-negative
                    Sequence[x]='0'
        f=open("data\\TrainingData\\%s\\%s.Sample%d.txt"%(Misician,Misician,order+i+1),'w')
        for notes in Sequence:
            f.write(notes+" ")
        f.close()        

'''
Function name: Import_Data
Task: import the training data and put them into a numpy array
Input:Musician
Output:a numpy array including all training data
'''
def Import_Data(Musician):
    Path_list=os.listdir("data\\TrainingData\\%s"%(Musician))
    Data=[[] for _ in range(len(Path_list))]
    for Sample in range(len(Path_list)):
        f=open("data\\TrainingData\\%s\\%s"%(Musician,Path_list[Sample]))
        Sequence=f.readlines()[0][:-1]  #eliminate empty element ''
        Data[Sample]=[int(x) for x in Sequence.split(' ')]
    return(np.array(Data))

#Load_Sequence('Mozart') #obtain training data

'''
Function name:Obtain_Train_Test_Data
Task: to obtain training data with the origin style which is corresponding to the particular musician
Input: musician
Output: origin data (other style) , target data (particular style)
'''
def Obtain_Train_Data(Musician):
    Musician_list=['Bach','Beethoven','Debussy','Schubert','Mozart','Hisaishi','Pianoboy','V.K']    #all available musicians
    Other_style=[x for x in Musician_list if x!= Musician_list] #defined as origin style
    Initialization=False
    for others in Other_style:
        if(Initialization==False):
            Origin_Data=Import_Data(others)
            Initialization=True
        else:
            Origin_Data=np.concatenate([Origin_Data,Import_Data(others)],axis=0)
    Target_Data=Import_Data(Musician)
    return Origin_Data,Target_Data


    
    