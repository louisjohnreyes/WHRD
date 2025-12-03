# mock_gpiozero.py

class Servo:
    def __init__(self, pin):
        self.pin = pin
        self._value = -1.0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if -1.0 <= new_value <= 1.0:
            self._value = new_value
        else:
            raise ValueError("Servo value must be between -1.0 and 1.0")

    def detach(self):
        print(f"Detaching servo on pin {self.pin}")
