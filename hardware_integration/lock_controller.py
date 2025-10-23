from hardware_integration.arduino import ArduinoLike
from utils.enums import DoorControls


# using this bridge in case i want to add more sensors and whatnot later
class LockController:
    def __init__(self, arduino):
        self.arduino: ArduinoLike = arduino

    def open(self):
        self.arduino.send_command(DoorControls.OPEN)

    def close(self):
        self.arduino.send_command(DoorControls.CLOSE)
