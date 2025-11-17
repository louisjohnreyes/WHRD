# Mock gpiozero library for testing on non-Raspberry Pi systems

class Servo:
    def __init__(self, pin):
        self._pin = pin
        self._value = 0
        print(f"Mock Servo initialized on pin {self._pin}")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if -1 <= new_value <= 1:
            self._value = new_value
            print(f"Mock Servo on pin {self._pin} set to {self._value}")
        else:
            raise ValueError("Servo value must be between -1 and 1")

    def detach(self):
        print(f"Detaching servo on pin {self._pin}")
