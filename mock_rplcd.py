class CharLCD:
    def __init__(self, i2c_expander, address, port, cols, rows, dotsize):
        pass

    def home(self):
        pass

    def write_string(self, value):
        pass

    def crlf(self):
        pass

    def clear(self):
        pass

    @property
    def cursor_pos(self):
        return (0, 0)

    @cursor_pos.setter
    def cursor_pos(self, value):
        pass
