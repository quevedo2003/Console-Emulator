import time
import uinput

def main():
    events = (
        uinput.KEY_A,
        uinput.KEY_S,
        uinput.KEY_W,
        uinput.KEY_D
    )

    with uinput.Device(events) as device:
        time.sleep(1) #this is here because machine needs time
        device.emit_click(uinput.KEY_A)
        device.emit_click(uinput.KEY_S)
        device.emit_click(uinput.KEY_W)
        device.emit_click(uinput.KEY_D)
        ##this was able to be made with the use of the examples folder given