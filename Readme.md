# CycleGANMusic

## Last update: 4/28/2019,18:57

To transfer the midi style with CycleGAN model, you need to prepare the midi file (for example, 'test.mid').

Then, run **\_\_init\_\_.py**:

`python __init__.py test.mid style`

The parameter **style** is the target style you want to generate (like `Mozart`). 

The final .mid file will be exported in **Output.mid**.