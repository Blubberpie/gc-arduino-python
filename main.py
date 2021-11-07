import arduino_utils
from serial_to_gamepad import Serial2Gamepad


if __name__ == '__main__':
    ser = arduino_utils.connect_arduino(baud_rate=115200)
    s2g = Serial2Gamepad(ser)
    s2g.start()
