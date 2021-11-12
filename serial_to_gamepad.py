import warnings
from serial import Serial
import vgamepad as vg

from button_mappings import ButtonMappings
from signal_handler import SignalHandler


class Serial2Gamepad:
    def __init__(self, ser: Serial, mode="x360", controller_choice=0):
        self.signal_handler = SignalHandler()
        self.ser = ser
        self.mode = mode
        self.inputs: list[int] = []
        self.controller_choice = controller_choice

        self.bm = ButtonMappings()

        print("Initializing gamepad...")
        if mode == "x360":
            self.game_pad = vg.VX360Gamepad()
        elif mode == "ds4":
            self.game_pad = vg.VDS4Gamepad()

    def _calculate_stick_output(self, stick: str, direction: int, gc_val: int) -> float:
        """
        direction: 0 = x, 1 = y
        """
        ret_val = (
                          (gc_val - self.bm.stick_thresholds.get(self.controller_choice)[stick][direction][0]) * 2
                          / self.bm.stick_thresholds.get(self.controller_choice)[stick][direction][2]
                  ) - 1
        return 1.0 if ret_val > 1.0 else -1.0 if ret_val < -1.0 else ret_val

    def _handle_triggers_and_sticks(self):
        # Handle Triggers
        if bool(self.inputs[self.bm.all_buttons_positions_mapping.get("lt")]):
            self.game_pad.left_trigger(255)
        else:
            self.game_pad.left_trigger(self.inputs[self.bm.all_buttons_positions_mapping.get("la")])

        if bool(self.inputs[self.bm.all_buttons_positions_mapping.get("rt")]):
            self.game_pad.right_trigger(255)
        else:
            self.game_pad.right_trigger(self.inputs[self.bm.all_buttons_positions_mapping.get("ra")])

        self.game_pad.update()

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

    def _send_inputs_x360(self):
        if len(self.inputs) > 0:
            # Handle Buttons
            for btn in self.bm.buttons_list_x360:
                if bool(self.inputs[self.bm.all_buttons_positions_mapping.get(btn)]):
                    self.game_pad.press_button(button=self.bm.button_values_x360.get(btn))
                else:
                    self.game_pad.release_button(button=self.bm.button_values_x360.get(btn))

            self._handle_triggers_and_sticks()
            self.game_pad.update()

    def _send_inputs_ds4(self):
        if len(self.inputs) > 0:
            # Handle Buttons
            for btn in self.bm.buttons_list_ds4:
                if bool(self.inputs[self.bm.all_buttons_positions_mapping.get(btn)]):
                    self.game_pad.press_button(button=self.bm.button_values_ds4.get(btn))
                else:
                    self.game_pad.release_button(button=self.bm.button_values_ds4.get(btn))

            self.game_pad.update()

            # Handle Hat
            d_pad_pressed = ""
            for btn in self.bm.d_pad_buttons_ds4:
                if bool(self.inputs[self.bm.all_buttons_positions_mapping.get(btn)]):
                    d_pad_pressed += btn

            if d_pad_pressed == "":
                self.game_pad.directional_pad(direction=0x8)
            else:
                self.game_pad.directional_pad(direction=self.bm.d_pad_values_ds4.get(d_pad_pressed))

            self._handle_triggers_and_sticks()
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
            if self.mode == "x360":
                self._send_inputs_x360()
            elif self.mode == "ds4":
                self._send_inputs_ds4()

    def start(self):
        self._loop()
