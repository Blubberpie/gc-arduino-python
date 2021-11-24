from threading import Thread, Event

from win32gui import GetForegroundWindow


class WinGUIThread(Thread):
    def __init__(self, my_window, stop_func, start_func):
        self.stop_event = Event()
        self.my_window = my_window
        self.stop_func = stop_func
        self.start_func = start_func
        super(WinGUIThread, self).__init__()

    def run(self):
        while not self.stop_event.is_set():
            self.main()

    def terminate(self):
        self.stop_event.set()

    def main(self):
        if GetForegroundWindow() != self.my_window:
            self.stop_func()
        else:
            self.start_func()

    def is_alive(self) -> bool:
        return not self.stop_event.is_set()
