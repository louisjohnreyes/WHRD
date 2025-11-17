class Servo:
    def __init__(self, pin):
        self.pin = pin
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        print(f"Mock Servo on pin {self.pin} set to {self._value}")

    def detach(self):
        print(f"Mock Servo on pin {self.pin} detached")
