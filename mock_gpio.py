BCM = 1
OUT = 1
IN = 1
PUD_UP = 1
HIGH = 1
LOW = 0

def setmode(mode):
    print("GPIO.setmode()")

def setup(pin, mode, pull_up_down=None):
    print(f"GPIO.setup({pin}, {mode})")

def output(pin, value):
    print(f"GPIO.output({pin}, {value})")

def input(pin):
    print(f"GPIO.input({pin})")
    return True

def cleanup():
    print("GPIO.cleanup()")
