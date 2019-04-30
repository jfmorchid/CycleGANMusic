# CycleGANMusic

## Last update: 4/30/2019,18:38

To transfer the midi style with CycleGAN model, you need to prepare the midi file (for example, 'test.mid').

Then, run **\_\_init\_\_.py**:

`python __init__.py test.mid style`

The parameter **style** is the target style you want to generate (like `Mozart`). 

The final .mid file will be exported in **Output.mid**.

## What's new in Version 1.1.0?

A new interface is designed to handle .json data from browser.

You need a .json data ( default `sequence.json` in the same folder ), and simply run this module:

`python infer_with_browser.py`

The ultimate effect is just the same as running **\_\_init\_\_.py**!