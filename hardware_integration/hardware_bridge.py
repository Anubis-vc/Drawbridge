from hardware_integration.arduino_handler import Arduino
from utils.enums import DoorControls


# using this bridge in case i want to add more sensors and whatnot later
class LockController:
    def __init__(self, arduino=None):
        self.arduino: Arduino = arduino or Arduino()

    def open(self):
        self.arduino.send_command(DoorControls.OPEN)

    def close(self):
        self.arduino.send_command(DoorControls.CLOSE)
