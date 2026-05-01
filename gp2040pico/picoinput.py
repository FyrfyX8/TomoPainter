import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Button Mapping

A = 3
B = 2
X = 17
Y = 4

L = 27
R = 22
ZL = 10
ZR = 9

HOME = 11

DPAD_UP = 0
DPAD_DOWN = 5
DPAD_RIGHT = 6
DPAD_LEFT = 13

def press(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def release(pin):
    GPIO.setup(pin, GPIO.IN)

def press_buttons(buttons : list[int], down : float = 0.1):
    for pin in buttons:
        press(pin)
    time.sleep(down)
    for pin in buttons:
        release(pin)

def connect():
    press(L)
    press(R)
    time.sleep(0.5)
    release(L)
    release(R)
    time.sleep(0.5)
