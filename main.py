from machine import Pin, ADC, PWM
import time

# RGB LED - Common Anode
red = PWM(Pin(14))
green = PWM(Pin(26))
blue = PWM(Pin(13))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

# Sensors
light_sensor = ADC(Pin(34))
light_sensor.atten(ADC.ATTN_11DB)
light_sensor.width(ADC.WIDTH_12BIT)

motion_sensor = Pin(27, Pin.IN)

# Button
button = Pin(25, Pin.IN, Pin.PULL_UP)

# Variables
mode = 0
last_button_state = 1
motion_timeout = 5
last_motion_time = 0

# Common Anode:
# 0 = OFF in our function
# 1023 = FULL brightness in our function
def set_color(r, g, b):
    red.duty(1023 - r)
    green.duty(1023 - g)
    blue.duty(1023 - b)

def off():
    set_color(0, 0, 0)

def fade_color(start, end, steps=50, delay=0.02):
    for i in range(steps + 1):
        r = int(start[0] + (end[0] - start[0]) * i / steps)
        g = int(start[1] + (end[1] - start[1]) * i / steps)
        b = int(start[2] + (end[2] - start[2]) * i / steps)
        set_color(r, g, b)
        time.sleep(delay)

current_color = (0, 0, 0)

def go_to_color(target):
    global current_color
    fade_color(current_color, target)
    current_color = target

print("RGB Smart Lighting System Running...")

while True:
    button_state = button.value()

    # Button changes mode
    if button_state == 0 and last_button_state == 1:
        mode += 1

        if mode > 2:
            mode = 0

        if mode == 0:
            print("MODE: AUTO")
        elif mode == 1:
            print("MODE: MANUAL ON")
        elif mode == 2:
            print("MODE: MANUAL OFF")

        time.sleep(0.3)

    last_button_state = button_state

    # AUTO MODE
    if mode == 0:
        light_value = light_sensor.read()
        motion = motion_sensor.value()

        print("Light:", light_value)
        print("Motion:", motion)

        # Bright environment
        if light_value < 1800:
            go_to_color((0, 0, 0))
            print("Bright -> RGB OFF")

        # Dark environment
        else:
            if motion == 1:
                last_motion_time = time.time()
                go_to_color((500, 500, 500))  # white, safe brightness
                print("Dark + Motion -> White")

            else:
                elapsed = time.time() - last_motion_time

                if elapsed < motion_timeout:
                    go_to_color((500, 500, 500))
                    print("Timeout -> Still White")

                else:
                    go_to_color((0, 0, 120))  # dim blue
                    print("Dark + No Motion -> Dim Blue")

    # MANUAL ON
    elif mode == 1:
        go_to_color((0, 500, 0))  # green
        print("MANUAL ON -> Green")

    # MANUAL OFF
    elif mode == 2:
        go_to_color((500, 0, 0))  # red status
        print("MANUAL OFF -> Red")

    print("----------------------")
    time.sleep(0.5)