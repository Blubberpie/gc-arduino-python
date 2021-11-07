import time
import warnings
from serial import Serial
import vgamepad as vg

from button_mappings import ButtonMappings
from signal_handler import SignalHandler


class Serial2Gamepad:
    def __init__(self, ser: Serial):
        self.signal_handler = SignalHandler()
        self.ser = ser
        self.inputs: list[int] = []

        self.bm = ButtonMappings()

        print("Initializing gamepad...")
        self.game_pad = vg.VX360Gamepad()

    def _calculate_stick_output(self, stick: str, direction: int, gc_val: int) -> float:
        """
        direction: 0 = x, 1 = y
        """
        ret_val = (
                          (gc_val - self.bm.stick_thresholds[stick][direction][0]) * 2
                          / self.bm.stick_thresholds[stick][direction][2]
                  ) - 1
        return 1.0 if ret_val > 1.0 else -1.0 if ret_val < -1.0 else ret_val

    def _send_inputs(self):
        if len(self.inputs) > 0:
            # Handle Buttons
            for btn in self.bm.buttons_list:
                if bool(self.inputs[self.bm.all_buttons_positions_mapping.get(btn)]):
                    self.game_pad.press_button(button=self.bm.button_values.get(btn))
                else:
                    self.game_pad.release_button(button=self.bm.button_values.get(btn))

            # Handle Triggers
            if bool(self.inputs[self.bm.all_buttons_positions_mapping.get("lt")]):
                self.game_pad.left_trigger(255)
            else:
                self.game_pad.left_trigger(self.inputs[self.bm.all_buttons_positions_mapping.get("la")])

            if bool(self.inputs[self.bm.all_buttons_positions_mapping.get("rt")]):
                self.game_pad.right_trigger(255)
            else:
                self.game_pad.right_trigger(self.inputs[self.bm.all_buttons_positions_mapping.get("ra")])

            # Handle Sticks
            self.game_pad.left_joystick_float(x_value_float=self._calculate_stick_output(
                stick="l",
                direction=0,
                gc_val=self.inputs[self.bm.all_buttons_positions_mapping.get("sx")]
            ), y_value_float=self._calculate_stick_output(
                stick="l",
                direction=1,
                gc_val=self.inputs[self.bm.all_buttons_positions_mapping.get("sy")]
            ))
            self.game_pad.right_joystick_float(x_value_float=self._calculate_stick_output(
                stick="c",
                direction=0,
                gc_val=self.inputs[self.bm.all_buttons_positions_mapping.get("cx")]
            ), y_value_float=self._calculate_stick_output(
                stick="c",
                direction=1,
                gc_val=self.inputs[self.bm.all_buttons_positions_mapping.get("cy")]
            ))

            self.game_pad.update()

    def _decode_serial(self, raw_data):
        if raw_data is not None:
            try:
                split_data = raw_data.split(",")
                if split_data[0] == "data":
                    self.inputs = list(map(int, split_data[1:]))
            except Exception as e:
                print(e)

    def _read_serial(self):
        try:
            return self.ser.read_until(b"\n", 255).decode().strip()
        except UnicodeDecodeError as e:
            warnings.warn("Invalid start byte - can happen at the start.")
            return

    def _loop(self):
        print("Reading from serial...")
        while not self.signal_handler.kill_now:
            raw_data = self._read_serial()
            self._decode_serial(raw_data)
            self._send_inputs()

    def start(self):
        self._loop()
