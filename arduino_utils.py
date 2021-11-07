import warnings
import serial
import time
import serial.tools.list_ports
from serial import Serial
from serial.tools.list_ports_common import ListPortInfo


def connect_arduino(baud_rate: int = 9600) -> Serial:
    def is_arduino(port: ListPortInfo) -> ListPortInfo:
        return port.manufacturer is not None and 'arduino' in port.manufacturer.lower()

    ports = serial.tools.list_ports.comports()
    arduino_ports = [port for port in ports if is_arduino(port)]

    def port2str(port) -> str:
        return f"{port.device} - {port.description} ({port.manufacturer})"

    if not arduino_ports:
        port_list = "\n".join([port2str(p) for p in ports])
        raise IOError(f"No Arduino found\n{port_list}")

    if len(arduino_ports) > 1:
        port_list = "\n".join([port2str(p) for p in ports])
        warnings.warn(f"Multiple Arduinos found - using the first\n{port_list}")

    selected_port = arduino_ports[0]
    print(f"Using {port2str(selected_port)}")
    ser = serial.Serial(selected_port.device, baud_rate)
    time.sleep(2)  # this is important it takes time to handshake
    return ser
