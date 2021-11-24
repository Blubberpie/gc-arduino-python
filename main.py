import arduino_utils
from serial_to_gamepad import Serial2Gamepad


if __name__ == '__main__':
    ser = arduino_utils.connect_arduino(baud_rate=115200)
    controller_mode = input("Controller mode (ds4, x360): ")
    s2g = Serial2Gamepad(
        ser,
        mode="ds4" if not controller_mode.strip() else controller_mode.strip()
    )
    s2g.start()
