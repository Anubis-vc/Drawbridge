import serial
import serial.tools.list_ports
import time


class Arduino:
    def __init__(self, baud_rate=9600, retries=3):
        self.baud_rate = baud_rate
        self.retries = retries
        self.serial = None  # will be set by the call to _connect()

        self.port = self._find_port()
        self._connect()

    def _find_port(self):
        """Find the correct arduino port even if we are not on desktop"""
        ports = serial.tools.list_ports.comports()
        if not ports:
            raise IOError("No ports found")

        for port in ports:
            # print(f"{port.description}\t{port.device}")
            if (
                "Arduino" in port.description
                or "CH340" in port.description
                or "ttyACM" in port.device
                or "usbmodem" in port.device
            ):
                print("Found Arduino")
                return port.device

        # startup should not succeed without this connection
        raise ModuleNotFoundError("Arduino not found")

    def _connect(self):
        for attempt in range(1, self.retries + 1):
            try:
                self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)

                # give arduino time to reset and wait for confirmation or 5 second timeout
                start_time = time.time()
                line = None
                while time.time() - start_time < 5 and not line:
                    line = self.read_line()
                    time.sleep(0.2)
                if line is None:
                    raise IOError("Arduino unable to set servo")

                print(f"Connected Arduino in {self.port} at {self.baud_rate} baud.")
                return
            except serial.SerialException as e:
                print(f"Attempt {attempt} failed: {e}")
                time.sleep(1)

        raise IOError("Failed to connect to Arduino after multiple attempts.")

    def send_command(self, command: str):
        """Send a string command followed by newline."""
        msg = (command.strip() + "\n").encode("utf-8")
        self.serial.write(msg)
        print("Sent: ", msg)  # When you add logging just set this to debug

    def read_line(self):
        """Read one line of response, does not wait for serial input."""
        if self.serial.in_waiting > 0:
            line = self.serial.readline().decode("utf-8").strip()
            print("Received: ", line)
            return line
        return None

    def close(self):
        """Close the serial connection if open."""
        try:
            self.serial.close()
        except Exception:
            print("Exception whle closing serial connection")
        finally:
            self.serial = None

    # Support usage as a context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
