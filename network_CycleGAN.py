'''
Module Name=network_CycleGAN
Function: to train a neuron network with CycleGAN algorithm
Remark: Environment: Windows 10, x86-64
        Frame: Keras , using tensorflow backend
        Refrence: https://arxiv.org/abs/1703.10593
        GAN: Generative Adversarial Networks    
        Notation declarations: we use T as target style, and O as original style 
'''

import keras
from keras.layers import Conv1D,MaxPool1D,Dense,Add,Activation,UpSampling1D,Input,Reshape
from keras.models import Model
from keras.constraints import min_max_norm
from keras.losses import mean_absolute_error,binary_crossentropy
from keras.callbacks import ReduceLROnPlateau
import numpy as np
from data_preprocessing import Obtain_Train_Data

'''
Function name:Id_Block
Task: a Resnet block of convolutional 1D layer
Input: a keras functional API , limitation of the parameter (<=0.09 default)
Output: antoher keras functional API
'''
def Id_Block(X,limit=0.09):
    X_copy=X           # the ResNet algorithm
    X=Conv1D(kernel_size=3,kernel_constraint=min_max_norm(0,limit),activation='relu',padding='same',filters=32)(X)
    X=Conv1D(kernel_size=3,kernel_constraint=min_max_norm(0,limit),activation='relu',padding='same',filters=32)(X)
    X=Conv1D(kernel_size=3,kernel_constraint=min_max_norm(0,limit),padding='same',filters=32)(X)
    X=Add()([X,X_copy])
    X=Activation('relu')(X)
    return X

'''
Function name:Encoder
Task: encoding with down-sampling convolution layer
Input: a keras functional API
Output: antoher keras functional API
'''
def Encoder(X):
    X=Id_Block(X,0.05)
    X=Id_Block(X,0.05)
    X=Id_Block(X,0.05)
    X=Id_Block(X,0.05)
    return X

'''
Function name:Decoder
Task: decoding with up-sampling convolution layer
Input: a keras functional API
Output: antoher keras functional API
'''
def Decoder(X):
    X=Id_Block(X,0.05)
    X=Id_Block(X,0.05)
    X=Id_Block(X,0.05)
    X=Conv1D(kernel_size=3,kernel_constraint=min_max_norm(0,0.05),activation='relu',padding='same',filters=1)(X)    
    return X    

'''
Function name:Discriminator
Task: a discriminator in GAN using dense
Input: a keras functional API
Output: antoher keras functional API
'''
def Discriminator(X):
    X=Id_Block(X)
    X=Id_Block(X)
    X=Id_Block(X)
    X=Conv1D(kernel_size=3,kernel_constraint=min_max_norm(0,0.09),activation='relu',padding='same',filters=1)(X)
    X=keras.layers.Reshape((900,))(X)
    X=Dense(80,activation='relu')(X)
    X=Dense(30,activation='relu')(X)
    X=Dense(1,activation='sigmoid')(X)
    return X

'''
Function name:Generater
Task: a generater in GAN with an encoder and a decoder
Input: a keras functional API
Output: antoher keras functional API
'''
def Generater(X):
    X=Encoder(X)
    X=Id_Block(X,0.05)
    X=Id_Block(X,0.05)
    X=Id_Block(X,0.05)   
    X=Decoder(X)
    return X

'''
Function name:Training_Discriminator
Task: to train a model of discriminator
Input: discriminator model, real data, fake data
Output: a trained model
'''
def Training_Discriminator(model,Real_data,Fake_data):
    label_1=np.ones((len(Real_data),1))       # the message of real data--"1"
    label_0=np.zeros((len(Fake_data),1))      # the massage of fake data--"0"
    Training_input=np.concatenate([Real_data,Fake_data],axis=0)
    Training_output=np.concatenate([label_1,label_0],axis=0)
    model.fit(Training_input,Training_output,epochs=3,batch_size=32)
    return model

'''
Function name:CycleGAN
Task: a cycleGAN neuron network
Input: Musician (corresponding to target style)
Output: the model from origin style to target style
Remart: meaning of CycyeGAN_T(O)_output*:
        output1: inputT->discriminatorT
        output2: inputT->generatorT_O->discriminatorO
        output3: inputT->generatorT_O->generatorO_T
        output4: inputT->generatorT_O (do not participate in error calculation)
'''
def CycleGAN(Musician):
    Optimizer_adam=keras.optimizers.adam(lr=0.003,decay=0.5)
    Train_dataset_O,Train_dataset_T=Obtain_Train_Data(Musician)
    Train_dataset_O=Train_dataset_O.reshape((len(Train_dataset_O),900,1))
    Train_dataset_T=Train_dataset_T.reshape((len(Train_dataset_T),900,1))
    T_input,O_input=Input((900,1,)),Input((900,1,))
    Disc_T_input,Disc_O_input=Input((900,1,)),Input((900,1,))
    Gen_T_O,Gen_O_T=Generater(T_input),Generater(O_input)   # T_O:target->origin , O_T:origin->target
    Gen_T_O_model=Model(inputs=T_input,outputs=Gen_T_O)
    Gen_O_T_model=Model(inputs=O_input,outputs=Gen_O_T)
    Disc_T,Disc_O=Discriminator(Disc_T_input),Discriminator(Disc_O_input)
    Disc_T_model=Model(inputs=Disc_T_input,outputs=Disc_T)
    Disc_T_model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])  # distriminator: target
    Disc_O_model=Model(inputs=Disc_O_input,outputs=Disc_O)
    Disc_O_model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])  # discriminator: origin 
    Training_Discriminator(Disc_O_model,Train_dataset_O,Train_dataset_T)    #use O data as real , T data as fake
    Training_Discriminator(Disc_T_model,Train_dataset_T,Train_dataset_O)    #use T data as real , O data as fake
    CycleGAN_T_input,CycleGAN_O_input=Input((900,1,)),Input((900,1,))   # next, two GAN networks are configured
    Disc_T.trainable,Disc_O.trainable=False,False #freeze discriminator
    
    
    CycleGAN_T_output1=Disc_T_model(CycleGAN_T_input)
    CycleGAN_T_output2=Disc_O_model(Gen_T_O_model(CycleGAN_T_input))
    CycleGAN_T_output3=Gen_O_T_model(Gen_T_O_model(CycleGAN_T_input))
    CycleGAN_T_output4=Gen_T_O_model(CycleGAN_T_input)
    CycleGAN_T_model=Model(inputs=CycleGAN_T_input,outputs=[CycleGAN_T_output1,CycleGAN_T_output2,CycleGAN_T_output3,CycleGAN_T_output4])
    CycleGAN_T_model.compile(optimizer=Optimizer_adam,loss=['binary_crossentropy','binary_crossentropy','mean_absolute_error','mean_absolute_error'],loss_weights=[0,100,1,0])
    
    CycleGAN_O_output1=Disc_O_model(CycleGAN_O_input)
    CycleGAN_O_output2=Disc_T_model(Gen_O_T_model(CycleGAN_O_input))
    CycleGAN_O_output3=Gen_T_O_model(Gen_O_T_model(CycleGAN_O_input))
    CycleGAN_O_output4=Gen_O_T_model(CycleGAN_O_input)
    CycleGAN_O_model=Model(inputs=CycleGAN_O_input,outputs=[CycleGAN_O_output1,CycleGAN_O_output2,CycleGAN_O_output3,CycleGAN_O_output4])
    CycleGAN_O_model.compile(optimizer=Optimizer_adam,loss=['binary_crossentropy','binary_crossentropy','mean_absolute_error','mean_absolute_error'],loss_weights=[0,100,1,0])
    
    for loop in range(120):     #cycle training -- 120 rounds
        print("Round %d:"%(loop+1))
        label_O,label_T=np.ones((len(Train_dataset_O),1)),np.ones((len(Train_dataset_T),1)) # "true" label
        CycleGAN_O_model.fit(Train_dataset_O,[label_O,label_O,Train_dataset_O,Train_dataset_O],epochs=2,batch_size=32)
        CycleGAN_T_model.fit(Train_dataset_T,[label_T,label_T,Train_dataset_T,Train_dataset_T],epochs=9,batch_size=32)
    CycleGAN_O_model.save("%s.hdf5"%(Musician))  #save the model

#CycleGAN('Hisaishi')