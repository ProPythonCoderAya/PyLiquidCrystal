try:
    from pyfirmata import Arduino
except (ModuleNotFoundError, IOError):
    import pip
    pip.main(['install', 'pyfirmata'])
    from pyfirmata import Arduino
import time


class LiquidCrystal:
    __doc__ = """Class LiquidCrystal."""

    def __init__(self, board: Arduino, rs: int, enable: int, d4: int, d5: int, d6: int, d7: int):
        self._board = board
        self._rs_pin = board.get_pin(f'd:{rs}:o')
        self._enable_pin = board.get_pin(f'd:{enable}:o')
        self._data_pins = [board.get_pin(f'd:{d4}:o'), board.get_pin(f'd:{d5}:o'), board.get_pin(f'd:{d6}:o'), board.get_pin(f'd:{d7}:o')]
        self._displayfunction = 0x08  # LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        self.begin(16, 1)
        time.sleep(0.5)

    def begin(self, cols: int, lines: int, dotsize=0x00):  # LCD_5x8DOTS
        if lines > 1:
            self._displayfunction |= 0x08  # LCD_2LINE
        self._numlines = lines
        self._row_offsets = [0x00, 0x40, 0x00 + cols, 0x40 + cols]

        # Wait 50 ms for the LCD to power up
        time.sleep(0.05)
        self.command(0x03)  # Function set
        time.sleep(0.005)
        self.command(0x03)  # Function set
        time.sleep(0.005)
        self.command(0x03)
        self.command(0x02)

        # Set # of lines and font size
        self.command(0x20 | self._displayfunction)
        time.sleep(0.1)
        self.display()
        time.sleep(0.1)
        self.clear()
        time.sleep(0.1)

    def setup_pin(self, pin):
        if pin is not None:
            # Replace with GPIO setup logic (e.g., RPi.GPIO)
            pass

    def command(self, value):
        self.send(value, False)

    def write(self, value):
        self.send(value, True)
        time.sleep(0.001)  # Allow the LCD to update.

    def send(self, value, mode):
        # Set RS pin
        self.set_pin(self._rs_pin, mode)
        time.sleep(0.00001)
        self.write4bits(value >> 4)
        self.write4bits(value & 0x0F)

    def write4bits(self, value):
        for i in range(4):
            self.set_pin(self._data_pins[i], (value >> i) & 0x01)
        self.pulse_enable()

    def pulse_enable(self):
        self.set_pin(self._enable_pin, False)
        time.sleep(0.00001)  # 1 microsecond
        self.set_pin(self._enable_pin, True)
        time.sleep(0.00001)
        self.set_pin(self._enable_pin, False)
        time.sleep(0.001)  # 100 microseconds

    def set_pin(self, pin, value):
        if pin is not None:
            pin.write(1 if value else 0)

    def clear(self):
        self.command(0x01)  # LCD_CLEARDISPLAY
        time.sleep(0.002)  # 2 milliseconds

    def display(self):
        self._displaycontrol = 0x04  # LCD_DISPLAYON
        self.command(0x08 | self._displaycontrol)

    def print(self, text: str):
        for char in text:
            self.write(ord(char))

    def setCursor(self, col, row):
        self.command(128 + col + (row * 40))
