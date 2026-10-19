import threading
import time

import serial


class ArduinoHandler:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self._lock = threading.Lock()

    def connect(self):
        if not self.port:
            print("ARDUINO_PORT not set, running without Arduino.")
            return
        try:
            with self._lock:
                if self.serial and self.serial.is_open:
                    return
                self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Uno resets when the port opens
            print(f"Arduino connected on {self.port}")
        except (serial.SerialException, OSError) as e:
            self.serial = None
            print(f"Arduino connection failed: {e}. AI can still run without Arduino.")

    def send(self, command: str):
        if command not in ("ON", "OFF"):
            print(f"Invalid Arduino command: {command}")
            return
        try:
            with self._lock:
                if not self.serial or not self.serial.is_open:
                    return
                self.serial.write((command + "\n").encode("utf-8"))
                self.serial.flush()
        except (serial.SerialException, OSError) as e:
            print(f"Arduino communication error: {e}")

    def close(self):
        try:
            with self._lock:
                if self.serial and self.serial.is_open:
                    self.serial.write(b"OFF\n")
                    self.serial.flush()
                    self.serial.close()
            self.serial = None
        except (serial.SerialException, OSError) as e:
            print(f"Error closing Arduino: {e}")