import threading
import time
import serial

class ArduinoHandler:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self._lock = threading.Lock()

    @property
    def connected(self) -> bool:
        return self.serial is not None and self.serial.is_open

    def connect(self) -> bool:
        if not self.port:
            print("[ARDUINO] ARDUINO_PORT not set, running without Arduino.")
            return False
        try:
            with self._lock:
                if self.connected:
                    return True
                self.serial = serial.Serial(
                    self.port, self.baudrate, timeout=1, write_timeout=1
                )
                time.sleep(2)  # Arduino may reset when the port opens
                self.serial.reset_input_buffer()
            print(f"[ARDUINO] Connected on {self.port}")
            return True
        except (serial.SerialException, OSError) as e:
            self.serial = None
            print(f"[ARDUINO] Connection failed: {e}. Running without Arduino.")
            return False

    def send(self, signal: str) -> bool:
        """Send a one-letter command: 'R' = reject (relay), 'X' = relay off."""
        with self._lock:
            if not self.connected:
                return False
            try:
                self.serial.write((signal + "\n").encode("ascii"))
                self.serial.flush()
                print(f"[CONTROL SIGNAL] Sent: {signal}")
                return True
            except (serial.SerialException, OSError) as e:
                print(f"[ARDUINO] Send error: {e}")
                return False

    def close(self):
        if self.connected:
            self.send("X")
            time.sleep(0.1)
        with self._lock:
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.serial = None
        print("[ARDUINO] Closed.")