# About

Reads Gamecube controller inputs with an Arduino, and outputs values to serial.
Python then reads and parses the serial output and uses the [vgamepad](https://pypi.org/project/vgamepad/)
library to output as X360 or DS4.

## NOTE

This is just a personal project, and is NOT meant to be optimized or well-documented. I just wanted
to make use of my GC controllers lying around.

## Hardware

- Arduino Uno
- Gamecube controller
  - You don't need to cut the wire like they tell you. You can stick a bunch of pins into the end of the male plug.
- 1k resistor

## Arduino

I used the library found at:

https://github.com/brownan/Gamecube-N64-Controller

and customized the code to print a specified data pattern to serial:
```
Example:
data,0,0,0,0,0,0,0,0,0,0,0,0,124,134,129,130,29,35

Order:
(tag),Start,Y,X,B,A,L,R,Z,D_UP,D_DOWN,D_RIGHT,D_LEFT,STICK_X,STICK_Y,C_X,C_Y,LT_ANALOG,RT_ANALOG
```

I ignored all the code for the N64 portion.

## Python

Just run `main.py`. You can change the thresholds of the sticks inside `button_mappings.py`.
