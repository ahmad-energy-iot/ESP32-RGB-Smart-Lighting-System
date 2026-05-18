# ESP32 RGB Smart Lighting System

---

#  Deutsche Version

## Projektbeschreibung

Dieses Projekt demonstriert ein intelligentes RGB-Beleuchtungssystem mit einem ESP32 Mikrocontroller, einem LDR-Lichtsensor, einem PIR-Bewegungssensor, einem RGB-LED und einem Push Button.

Das System erkennt automatisch die Umgebungshelligkeit und Bewegungen. Abhängig von der Situation wird eine passende RGB-Farbe aktiviert. Zusätzlich kann der Benutzer über einen Push Button zwischen verschiedenen Betriebsmodi wechseln.

Dieses Projekt zeigt wichtige Grundlagen aus den Bereichen IoT, Smart Home, Sensorik, PWM-Steuerung und energieeffiziente Beleuchtung.

---

## Hauptfunktionen

- Automatische Lichtsteuerung mit LDR-Sensor
- Bewegungserkennung mit PIR-Sensor
- RGB-Farbsteuerung mit PWM
- Sanfte Farb- und Helligkeitsübergänge
- Automatischer Modus
- Manueller EIN-Modus
- Manueller AUS-Modus
- Visuelle Statusanzeige über Farben
- Energieeffiziente Beleuchtungslogik

---

## Verwendete Komponenten

| Komponente | Beschreibung |
|---|---|
| ESP32 DevKit V1 | Hauptcontroller des Systems |
| LDR Sensor | Misst die Umgebungshelligkeit |
| PIR Motion Sensor | Erkennt Bewegungen |
| RGB LED | Mehrfarbige Status- und Beleuchtungsanzeige |
| Push Button | Umschalten zwischen den Betriebsmodi |
| Widerstände | Schutz für die RGB-LED Kanäle |
| Breadboard | Aufbau der Schaltung |
| Jumper Kabel | Elektrische Verbindungen |

---

## Pin-Verbindungen

| Komponente | ESP32 Pin |
|---|---|
| RGB Rot | GPIO14 |
| RGB Grün | GPIO26 |
| RGB Blau | GPIO13 |
| RGB Common Anode | 3V3 |
| LDR Sensor AO | GPIO34 |
| PIR Sensor OUT | GPIO27 |
| Push Button | GPIO25 |
| Button GND | GND |

---

## RGB LED Typ

In diesem Projekt wird ein RGB LED mit Common Anode verwendet.

Das bedeutet:

- Das lange Bein des RGB LEDs wird mit 3V3 verbunden.
- Die drei anderen Beine werden über Widerstände mit GPIO Pins verbunden.
- Die Logik ist invertiert:
  - GPIO LOW bedeutet LED-Kanal EIN.
  - GPIO HIGH bedeutet LED-Kanal AUS.

Im Code wird diese invertierte Logik automatisch über die Funktion `set_color()` korrigiert.

---

## Farblogik des Systems

| Situation | Farbe | Bedeutung |
|---|---|---|
| Helle Umgebung | AUS | Es ist genug Licht vorhanden |
| Dunkelheit ohne Bewegung | Blau | Nacht-Standby-Modus |
| Dunkelheit mit Bewegung | Weiß | Bewegung erkannt |
| Manual ON | Grün | Beleuchtung manuell eingeschaltet |
| Manual OFF | Rot | System manuell ausgeschaltet |

---

## Betriebsmodi

| Modus | Beschreibung |
|---|---|
| AUTO MODE | Sensoren steuern das Licht automatisch |
| MANUAL ON | RGB LED bleibt manuell eingeschaltet |
| MANUAL OFF | RGB LED zeigt roten Statusmodus |

Der Push Button wechselt bei jedem Tastendruck zwischen den Modi:

```text
AUTO MODE → MANUAL ON → MANUAL OFF → AUTO MODE
```

---

## Systemlogik

1. Der LDR-Sensor misst die Umgebungshelligkeit.
2. Wenn genug Licht vorhanden ist, bleibt das RGB LED ausgeschaltet.
3. Wenn es dunkel ist, prüft der ESP32 den PIR-Bewegungssensor.
4. Wenn keine Bewegung erkannt wird, leuchtet das RGB LED schwach blau.
5. Wenn Bewegung erkannt wird, leuchtet das RGB LED weiß.
6. Mit dem Button kann der Benutzer manuell zwischen AUTO, ON und OFF wechseln.
7. Die Farbänderungen erfolgen mit sanften Übergängen.

---

## Nutzen des Projekts

Dieses Projekt kann in vielen praktischen Bereichen verwendet werden:

- Smart Home Beleuchtung
- Automatische Flurbeleuchtung
- Treppenhausbeleuchtung
- Sicherheitsbeleuchtung
- Garagenbeleuchtung
- Energieeffiziente Gebäudesteuerung
- Solarbetriebene Lichtsysteme
- Smart-City Beleuchtung
- IoT-Lernprojekte
- Renewable-Energy Anwendungen
- Bewegungsgesteuerte Beleuchtung

Das Projekt zeigt, wie intelligente Systeme Energie sparen können, indem Licht nur dann aktiviert wird, wenn es wirklich benötigt wird.

---

## MicroPython Code

```python
from machine import Pin, ADC, PWM
import time

# =========================================
# RGB LED - Common Anode
# =========================================
red = PWM(Pin(14))
green = PWM(Pin(26))
blue = PWM(Pin(13))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

# =========================================
# Light Sensor LDR on GPIO34
# =========================================
light_sensor = ADC(Pin(34))
light_sensor.atten(ADC.ATTN_11DB)
light_sensor.width(ADC.WIDTH_12BIT)

# =========================================
# PIR Motion Sensor on GPIO27
# =========================================
motion_sensor = Pin(27, Pin.IN)

# =========================================
# Push Button on GPIO25
# =========================================
button = Pin(25, Pin.IN, Pin.PULL_UP)

# =========================================
# Variables
# =========================================
mode = 0
last_button_state = 1

motion_timeout = 5
last_motion_time = 0

current_color = (0, 0, 0)

# =========================================
# Common Anode RGB Function
# 0 = OFF in this function
# 1023 = FULL brightness in this function
# =========================================
def set_color(r, g, b):
    red.duty(1023 - r)
    green.duty(1023 - g)
    blue.duty(1023 - b)

# =========================================
# Smooth Fade Function
# =========================================
def fade_color(start, end, steps=50, delay=0.02):
    for i in range(steps + 1):
        r = int(start[0] + (end[0] - start[0]) * i / steps)
        g = int(start[1] + (end[1] - start[1]) * i / steps)
        b = int(start[2] + (end[2] - start[2]) * i / steps)

        set_color(r, g, b)
        time.sleep(delay)

# =========================================
# Move Smoothly to Target Color
# =========================================
def go_to_color(target):
    global current_color

    if current_color != target:
        fade_color(current_color, target)
        current_color = target

print("ESP32 RGB Smart Lighting System Running...")

while True:

    # =====================================
    # Button Reading
    # =====================================
    button_state = button.value()

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

    # =====================================
    # AUTO MODE
    # =====================================
    if mode == 0:

        light_value = light_sensor.read()
        motion = motion_sensor.value()

        print("Light:", light_value)
        print("Motion:", motion)

        # Bright environment
        if light_value < 1800:
            go_to_color((0, 0, 0))
            print("Bright Environment -> RGB OFF")

        # Dark environment
        else:

            # Motion detected
            if motion == 1:
                last_motion_time = time.time()
                go_to_color((500, 500, 500))
                print("Dark + Motion -> White")

            # No motion
            else:
                elapsed = time.time() - last_motion_time

                if elapsed < motion_timeout:
                    go_to_color((500, 500, 500))
                    print("Timeout -> Still White")

                else:
                    go_to_color((0, 0, 120))
                    print("Dark + No Motion -> Dim Blue")

    # =====================================
    # MANUAL ON MODE
    # =====================================
    elif mode == 1:
        go_to_color((0, 500, 0))
        print("MANUAL ON -> Green")

    # =====================================
    # MANUAL OFF MODE
    # =====================================
    elif mode == 2:
        go_to_color((500, 0, 0))
        print("MANUAL OFF -> Red")

    print("----------------------")
    time.sleep(0.5)
```

---

#  English Version

## Project Description

This project demonstrates an intelligent RGB lighting system using an ESP32 microcontroller, an LDR light sensor, a PIR motion sensor, an RGB LED, and a push button.

The system automatically detects ambient light and motion. Depending on the situation, a suitable RGB color is activated. The user can also switch between different operating modes using the push button.

This project demonstrates important fundamentals of IoT, Smart Home systems, sensor integration, PWM control, and energy-efficient lighting.

---

## Main Features

- Automatic lighting control using an LDR sensor
- Motion detection using a PIR sensor
- RGB color control using PWM
- Smooth color and brightness transitions
- Automatic mode
- Manual ON mode
- Manual OFF mode
- Visual status indication using colors
- Energy-efficient lighting logic

---

## Components Used

| Component | Description |
|---|---|
| ESP32 DevKit V1 | Main controller of the system |
| LDR Sensor | Measures ambient light intensity |
| PIR Motion Sensor | Detects movement |
| RGB LED | Multicolor lighting and status indicator |
| Push Button | Switches between operating modes |
| Resistors | Protect the RGB LED channels |
| Breadboard | Circuit assembly |
| Jumper Wires | Electrical connections |

---

## Pin Connections

| Component | ESP32 Pin |
|---|---|
| RGB Red | GPIO14 |
| RGB Green | GPIO26 |
| RGB Blue | GPIO13 |
| RGB Common Anode | 3V3 |
| LDR Sensor AO | GPIO34 |
| PIR Sensor OUT | GPIO27 |
| Push Button | GPIO25 |
| Button GND | GND |

---

## RGB LED Type

This project uses a Common Anode RGB LED.

This means:

- The long leg of the RGB LED is connected to 3V3.
- The other three legs are connected to GPIO pins through resistors.
- The logic is inverted:
  - GPIO LOW means LED channel ON.
  - GPIO HIGH means LED channel OFF.

The function `set_color()` automatically handles this inverted logic.

---

## System Color Logic

| Situation | Color | Meaning |
|---|---|---|
| Bright environment | OFF | Enough light is available |
| Dark without motion | Blue | Night standby mode |
| Dark with motion | White | Motion detected |
| Manual ON | Green | Lighting manually enabled |
| Manual OFF | Red | System manually disabled |

---

## Operating Modes

| Mode | Description |
|---|---|
| AUTO MODE | Sensors control the lighting automatically |
| MANUAL ON | RGB LED stays manually enabled |
| MANUAL OFF | RGB LED shows red status mode |

Each button press changes the mode:

```text
AUTO MODE → MANUAL ON → MANUAL OFF → AUTO MODE
```

---

## System Logic

1. The LDR sensor measures ambient brightness.
2. If enough light is available, the RGB LED remains OFF.
3. If it is dark, the ESP32 checks the PIR motion sensor.
4. If no motion is detected, the RGB LED glows dim blue.
5. If motion is detected, the RGB LED turns white.
6. The button allows the user to switch manually between AUTO, ON, and OFF modes.
7. Color changes are performed smoothly using fade transitions.

---

## Project Benefits

This project can be used in many real-life applications:

- Smart Home lighting
- Automatic hallway lighting
- Staircase lighting
- Security lighting
- Garage lighting
- Energy-efficient building automation
- Solar-powered lighting systems
- Smart City lighting
- IoT learning projects
- Renewable Energy applications
- Motion-based lighting systems

The project demonstrates how intelligent systems can save energy by activating lighting only when it is actually needed.

---

## MicroPython Code

```python
from machine import Pin, ADC, PWM
import time

# =========================================
# RGB LED - Common Anode
# =========================================
red = PWM(Pin(14))
green = PWM(Pin(26))
blue = PWM(Pin(13))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

# =========================================
# Light Sensor LDR on GPIO34
# =========================================
light_sensor = ADC(Pin(34))
light_sensor.atten(ADC.ATTN_11DB)
light_sensor.width(ADC.WIDTH_12BIT)

# =========================================
# PIR Motion Sensor on GPIO27
# =========================================
motion_sensor = Pin(27, Pin.IN)

# =========================================
# Push Button on GPIO25
# =========================================
button = Pin(25, Pin.IN, Pin.PULL_UP)

# =========================================
# Variables
# =========================================
mode = 0
last_button_state = 1

motion_timeout = 5
last_motion_time = 0

current_color = (0, 0, 0)

# =========================================
# Common Anode RGB Function
# 0 = OFF in this function
# 1023 = FULL brightness in this function
# =========================================
def set_color(r, g, b):
    red.duty(1023 - r)
    green.duty(1023 - g)
    blue.duty(1023 - b)

# =========================================
# Smooth Fade Function
# =========================================
def fade_color(start, end, steps=50, delay=0.02):
    for i in range(steps + 1):
        r = int(start[0] + (end[0] - start[0]) * i / steps)
        g = int(start[1] + (end[1] - start[1]) * i / steps)
        b = int(start[2] + (end[2] - start[2]) * i / steps)

        set_color(r, g, b)
        time.sleep(delay)

# =========================================
# Move Smoothly to Target Color
# =========================================
def go_to_color(target):
    global current_color

    if current_color != target:
        fade_color(current_color, target)
        current_color = target

print("ESP32 RGB Smart Lighting System Running...")

while True:

    # =====================================
    # Button Reading
    # =====================================
    button_state = button.value()

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

    # =====================================
    # AUTO MODE
    # =====================================
    if mode == 0:

        light_value = light_sensor.read()
        motion = motion_sensor.value()

        print("Light:", light_value)
        print("Motion:", motion)

        # Bright environment
        if light_value < 1800:
            go_to_color((0, 0, 0))
            print("Bright Environment -> RGB OFF")

        # Dark environment
        else:

            # Motion detected
            if motion == 1:
                last_motion_time = time.time()
                go_to_color((500, 500, 500))
                print("Dark + Motion -> White")

            # No motion
            else:
                elapsed = time.time() - last_motion_time

                if elapsed < motion_timeout:
                    go_to_color((500, 500, 500))
                    print("Timeout -> Still White")

                else:
                    go_to_color((0, 0, 120))
                    print("Dark + No Motion -> Dim Blue")

    # =====================================
    # MANUAL ON MODE
    # =====================================
    elif mode == 1:
        go_to_color((0, 500, 0))
        print("MANUAL ON -> Green")

    # =====================================
    # MANUAL OFF MODE
    # =====================================
    elif mode == 2:
        go_to_color((500, 0, 0))
        print("MANUAL OFF -> Red")

    print("----------------------")
    time.sleep(0.5)
```

---

## Developer

**Ahmad Azroun**  
Renewable Energy Manager | IoT & Smart Energy Systems Developer
