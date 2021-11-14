import arduino_utils
from serial_to_gamepad import Serial2Gamepad


if __name__ == '__main__':
    ser = arduino_utils.connect_arduino(baud_rate=115200)
    controller_mode = input("Controller mode (ds4, x360): ")
    controller_choice = input("Controller preset: ")
    s2g = Serial2Gamepad(
        ser,
        mode="ds4" if not controller_mode.strip() else controller_mode.strip(),
        controller_choice=1 if not controller_choice.strip() else int(controller_choice)
    )
    s2g.start()
