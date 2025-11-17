class Servo:
    def __init__(self, pin):
        print(f"Mock Servo initialized on pin {pin}")
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        print(f"Mock Servo value set to {new_value}")
        self._value = new_value
