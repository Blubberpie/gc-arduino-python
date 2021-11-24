import json
import os
import warnings
from typing import Optional

import vgamepad as vg
from pynput.keyboard import Listener, KeyCode
from serial import Serial
from win32gui import GetForegroundWindow

from button_mappings import ButtonMappings
from signal_handler import SignalHandler
from win_gui_thread import WinGUIThread

_current_window = None


class Serial2Gamepad:

    def __init__(self, ser: Serial, mode="ds4"):
        global _current_window
        _current_window = GetForegroundWindow()
        self.signal_handler = SignalHandler()
        self.ser = ser
        self.mode = mode
        self.inputs: list[int] = []
        self.bm = ButtonMappings()
        self.key_listener: Optional[Listener] = None
        self._initialize_key_listener()
        self.win_gui_thread = WinGUIThread(
            _current_window,
            self._handle_stop_key_listener,
            self._handle_start_key_listener
        )
        self.win_gui_thread.start()

        self.calibrating = False
        self.config_file = "config.json"
        self._load_calibration_file()

        print("Initializing gamepad...")
        if mode == "x360":
            self.game_pad = vg.VX360Gamepad()
        elif mode == "ds4":
            self.game_pad = vg.VDS4Gamepad()

    def _initialize_key_listener(self):
        if self.key_listener is not None and self.key_listener.running:
            self.key_listener.stop()
        self.key_listener = Listener(on_press=self._handle_key_press, on_release=self._handle_key_release)
        self.key_listener.start()

    def _handle_stop_key_listener(self):
        if self.key_listener.running:
            self.key_listener.stop()

    def _handle_start_key_listener(self):
        if not self.key_listener.running:
            self._initialize_key_listener()

    def _handle_key_press(self, key):
        pass

    def _handle_key_release(self, key):
        if key == KeyCode.from_char('c'):
            self.calibrating = True
        if key == KeyCode.from_char('q'):
            if self.calibrating:
                print("Cancelling calibration")
                self.calibrating = False

    def _load_calibration_file(self):
        def set_values():
            for stick_type, values in self.config["stick_calibration"].items():
                self.config["stick_calibration"][stick_type]["x_range"] = values["x_max"] - values["x_min"]
                self.config["stick_calibration"][stick_type]["y_range"] = values["y_max"] - values["y_min"]
                self.config["stick_calibration"][stick_type]["x_center"] = (values["x_min"] + values["x_max"]) // 2
                self.config["stick_calibration"][stick_type]["y_center"] = (values["y_max"] + values["y_min"]) // 2
                dead_zone_x = self.config["stick_calibration"][stick_type]["x_center"] * self.config["dead_zone"]
                self.config[f"{stick_type}_dead_zone_x_min"] = \
                    self.config["stick_calibration"][stick_type]["x_center"] - dead_zone_x
                self.config[f"{stick_type}_dead_zone_x_max"] = \
                    self.config["stick_calibration"][stick_type]["x_center"] + dead_zone_x
                dead_zone_y = self.config["stick_calibration"][stick_type]["y_center"] * self.config["dead_zone"]
                self.config[f"{stick_type}_dead_zone_y_min"] = \
                    self.config["stick_calibration"][stick_type]["y_center"] - dead_zone_y
                self.config[f"{stick_type}_dead_zone_y_max"] = \
                    self.config["stick_calibration"][stick_type]["y_center"] + dead_zone_y

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    set_values()
            else:
                self.config = self.bm.config
                set_values()
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f)

        except Exception as e:
            print(f"Error reading calibration file! | {e}")
            exit(0)

    def _calibrate_stick(self, stick: str):
        x_min, x_max, y_min, y_max = 255, 0, 255, 0
        stick_name = stick.upper() + 'eft' if stick == 'l' else stick.upper()

        def commit():
            print("Committing calibration...")
            target_stick = self.config["stick_calibration"][stick]
            target_stick["x_min"], target_stick["x_max"], target_stick["y_min"], target_stick["y_max"] = x_min, x_max, y_min, y_max
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
            self._load_calibration_file()
            print(f"{stick_name}-Stick has been calibrated.")

        print(f"Calibrating {stick_name}-Stick...")
        print(f"Tilt and rotate the {stick_name}-Stick until all sides have been covered. Press A when done.")
        a_last = 0
        while True:
            self._decode_serial(self._read_serial())
            a_cur = self.inputs[self.bm.all_buttons_positions_mapping.get('a')]

            if a_cur - a_last < 0:
                break
            elif not self.calibrating:
                return
            else:
                cur_x = self.inputs[self.bm.all_buttons_positions_mapping.get(f"{'s' if stick == 'l' else stick}x")]
                cur_y = self.inputs[self.bm.all_buttons_positions_mapping.get(f"{'s' if stick == 'l' else stick}y")]

                x_min = min(x_min, cur_x)
                x_max = max(x_max, cur_x)
                y_min = min(y_min, cur_y)
                y_max = max(y_max, cur_y)

                a_last = a_cur

        print(f"X range: {x_min}, {x_max}")
        print(f"Y range: {y_min}, {y_max}")

        if self.calibrating:
            commit()

    def _calibrate(self):
        print("\nBeginning calibration. Press Q to cancel.")
        self._calibrate_stick("l")
        self._calibrate_stick("c")
        self.calibrating = False

    def _calculate_stick_output(self, stick: str, direction: int, gc_val: int) -> float:
        direction_map = {0: "x", 1: "y"}
        stick_config = self.config["stick_calibration"][stick]
        axis = direction_map[direction]

        if self.config[f"{stick}_dead_zone_{axis}_min"] <= gc_val <= self.config[f"{stick}_dead_zone_{axis}_max"]:
            return 0.0
        ret_val = ((gc_val - stick_config[f"{axis}_min"]) * 2 / stick_config[f"{axis}_range"]) - 1

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
            direction=0,  # x
            gc_val=self.inputs[self.bm.all_buttons_positions_mapping.get("sx")]
        ), y_value_float=self._calculate_stick_output(
            stick="l",
            direction=1,  # y
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
        try:
            # Handle Buttons
            for btn in self.bm.buttons_list_x360:
                if bool(self.inputs[self.bm.all_buttons_positions_mapping.get(btn)]):
                    self.game_pad.press_button(button=self.bm.button_values_x360.get(btn))
                else:
                    self.game_pad.release_button(button=self.bm.button_values_x360.get(btn))

            self._handle_triggers_and_sticks()
            self.game_pad.update()
        except IndexError as e:
            print("Error reading input. Continuing...")

    def _send_inputs_ds4(self):
        try:
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
        except IndexError as e:
            print(f"Error reading input. Continuing... | {e}")
        except Exception as e:
            print(f"Unknown error | {e}")

    def _decode_serial(self, raw_data):
        if raw_data is not None:
            try:
                split_data = raw_data.split(",")
                if split_data[0] == "data":
                    self.inputs = list(map(int, split_data[1:]))
            except Exception as e:
                print(f"Decoding error: {e}")

    def _read_serial(self):
        try:
            return self.ser.read_until(b"\n", 255).decode().strip()
        except UnicodeDecodeError as e:
            warnings.warn("Invalid start byte - can happen at the start.")
            return

    def _loop(self):
        print("\nPress C to begin calibrating control sticks")
        print("Reading from serial...")
        senders = {
            'x360': self._send_inputs_x360,
            'ds4': self._send_inputs_ds4
        }

        self.calibrating = False  # Override key press
        while not self.signal_handler.kill_now:
            if self.calibrating:
                self._calibrate()
            else:
                raw_data = self._read_serial()
                self._decode_serial(raw_data)
                senders[self.mode]()

        if self.signal_handler.kill_now:
            self.key_listener.stop()
            self.win_gui_thread.terminate()

    def start(self):
        self._loop()
