from hardware_integration.arduino import ArduinoLike


class MockArduino(ArduinoLike):
    def __init__(self):
        print("Created mock arduino")

    def send_command(self, command: str):
        print("Sent mock: ", command)  # When you add logging just set this to debug

    def read_line(self):
        return "Mock Read"

    def close(self):
        pass

    # Support usage as a context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
