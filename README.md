# Python and Arduino Serial Communication Demo

## Requirement

- Python3
- [PySerial](https://pythonhosted.org/pyserial/)
- [matplotlib](https://matplotlib.org/)

This should work (if your python3's pip is at pip3 use pip3 instead of pip)
```
pip install pyserial matplotlib
```

## LightSwitch

Find matching sketch at
https://create.arduino.cc/editor/piti118/d62e2b1e-f304-48b8-99cd-0d57f0375e1c/preview
- barebone.py contains minimal code on how to talk to arduino
- lightswitch.py simple GUI based on tkinter for turning on/off LED

## Realtime Plotting With Matplotlib

Find matching sketch at https://create.arduino.cc/editor/piti118/9c083788-4653-48a6-860b-28302d9626ea/preview

- streaming.py a simple gui which plot stuff in real time.

Note that this uses a crazy baudrate of 250000. If the data get corrupted too often use lower baudrate.
