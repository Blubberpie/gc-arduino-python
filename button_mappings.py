class ButtonMappings:
    all_buttons_list = ["s", "y", "x", "b", "a", "lt", "rt", "z", "u", "d", "r", "l", "sx", "sy", "cx", "cy", "la", "ra"]
    all_buttons_positions_mapping = dict(zip(all_buttons_list, range(len(all_buttons_list))))

    buttons_list = ["s", "y", "x", "b", "a", "z", "u", "d", "r", "l"]
    button_values = {
        "s": 0x0010,
        "y": 0x8000,
        "x": 0x4000,
        "b": 0x2000,
        "a": 0x1000,
        "z": 0x0200,
        "u": 0x0001,
        "d": 0x0002,
        "r": 0x0008,
        "l": 0x0004
    }
    stick_thresholds = {
        "l": ((26, 229, 229-26), (61, 216, 216-61)),
        "c": ((45, 208, 208-45), (49, 213, 213-49))
    }
