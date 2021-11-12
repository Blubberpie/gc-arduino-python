class ButtonMappings:
    all_buttons_list = ["s", "y", "x", "b", "a", "lt", "rt", "z", "u", "d", "r", "l", "sx", "sy", "cx", "cy", "la", "ra"]
    all_buttons_positions_mapping = dict(zip(all_buttons_list, range(len(all_buttons_list))))

    buttons_list_x360 = ["s", "y", "x", "b", "a", "z", "u", "d", "r", "l"]
    buttons_list_ds4 = ["s", "y", "x", "b", "a", "lt", "rt", "z"]

    button_values_x360 = {
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
    button_values_ds4 = {
        "s": 1 << 13,
        "y": 1 << 7,
        "x": 1 << 4,
        "b": 1 << 6,
        "a": 1 << 5,
        "z": 1 << 9,
        "lt": 1 << 10,
        "rt": 1 << 11
    }
    d_pad_buttons_ds4 = ["u", "d", "r", "l"]
    d_pad_values_ds4 = {
        "u": 0x0,
        "d": 0x4,
        "r": 0x2,
        "l": 0x6,
        "ur": 0x1,
        "ul": 0x7,
        "dr": 0x3,
        "dl": 0x5
    }
    stick_thresholds = {
        0: {
            "l": ((26, 229, 229-26), (61, 216, 216-61)),
            "c": ((45, 208, 208-45), (49, 213, 213-49))
        },
        1: {
            "l": ((27, 224, 224-27), (46, 221, 221-46)),
            "c": ((43, 209, 209-43), (38, 212, 212-38))
        }
    }
