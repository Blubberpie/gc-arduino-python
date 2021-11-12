import arduino_utils
from serial_to_gamepad import Serial2Gamepad


if __name__ == '__main__':
    ser = arduino_utils.connect_arduino(baud_rate=115200)
    s2g = Serial2Gamepad(
        ser,
        mode=input("Controller mode (ds4, x360): "),
        controller_choice=int(input("Controller preset: "))
    )
    s2g.start()
