import time
import digitalio
import board
import usb_hid
import rotaryio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

def setup_button(pin, pull=digitalio.Pull.DOWN):
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = pull
    return button

def setup_encoder(channel_a, channel_b, btn_pin, divisor=2):
    encoder = rotaryio.IncrementalEncoder(channel_a, channel_b, divisor=divisor)
    button = setup_button(btn_pin, pull=digitalio.Pull.UP)  # Set encoder button to pull-up
    return encoder, button

#encoder: rotational pos, buttonE: z
encoder, buttonE = setup_encoder(board.GP22, board.GP21, board.GP20)
buttons = [setup_button(pin) for pin in (board.GP19, board.GP18, board.GP17, board.GP16)]

keyboard = ConsumerControl(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)

last_position = encoder.position
button_state = False

while True:
    current_position = encoder.position
    if current_position != last_position:
        key = ConsumerControlCode.VOLUME_DECREMENT if current_position > last_position else ConsumerControlCode.VOLUME_INCREMENT
        keyboard.send(key * abs(current_position - last_position))
        last_position = current_position
        print(current_position)
    if not buttonE.value and not button_state: 
        # print("Button pressed.")
        keyboard.send(ConsumerControlCode.PLAY_PAUSE)
        button_state = True  # Update button state
    if buttonE.value and button_state:  
        button_state = False
    for button, btn_pin in zip(buttons, (board.GP19, board.GP18, board.GP17, board.GP16)):
        if button.value:
            key_sequence ={
                board.GP19: (Keycode.CONTROL, Keycode.SHIFT, Keycode.TAB),
                board.GP18: (Keycode.CONTROL, Keycode.TAB),
                board.GP17: (Keycode.ALT, Keycode.TAB),
                board.GP16: (Keycode.GUI, Keycode.L)
            }.get(btn_pin, ())
            kbd.send(*key_sequence)
            # print("Button Pressed", key_sequence)
            time.sleep(0.25)
        # break
