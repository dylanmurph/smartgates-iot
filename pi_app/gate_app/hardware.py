import time
import threading
from gpiozero import OutputDevice, MotionSensor, DigitalInputDevice, PWMOutputDevice, Button, LED

# --- CONFIGURATION & PINS ---
RELAY_PIN = 17
BUZZER_PIN = 23
PIR_PIN = 16
LDR_PIN = 21
GATE_SENSOR_PIN = 25

LED_RED_PIN = 24
LED_YELLOW_PIN = 19
LED_GREEN_PIN = 26

SIREN_FREQ_START = 500
SIREN_FREQ_END = 2500
RELAY_DURATION = 5

relay = OutputDevice(RELAY_PIN, active_high=True, initial_value=False)
buzzer = PWMOutputDevice(BUZZER_PIN, frequency=1000, initial_value=0)
pir = MotionSensor(PIR_PIN, queue_len=5)
ldr = DigitalInputDevice(LDR_PIN, bounce_time=0.3)
gate_switch = Button(GATE_SENSOR_PIN, pull_up=True, bounce_time=0.3)

red = LED(LED_RED_PIN)
yellow = LED(LED_YELLOW_PIN)
green = LED(LED_GREEN_PIN)

_siren_active = False
_relay_active = False

def _siren_loop():
    global _siren_active
    while _siren_active:
        red.toggle()

        # Rising Tone
        for freq in range(SIREN_FREQ_START, SIREN_FREQ_END, 100):
            if not _siren_active: break
            buzzer.frequency = freq
            buzzer.value = 0.5
            time.sleep(0.02)

        # Falling Tone
        for freq in range(SIREN_FREQ_END, SIREN_FREQ_START, -100):
            if not _siren_active: break
            buzzer.frequency = freq
            buzzer.value = 0.5
            time.sleep(0.02)

    buzzer.off()
    red.off()
    if gate_switch.is_pressed:
        green.on()
    else:
        red.on()

def start_siren():
    global _siren_active
    if not _siren_active:
        _siren_active = True
        green.off()
        yellow.off()
        t = threading.Thread(target=_siren_loop)
        t.start()

def stop_siren():
    global _siren_active
    _siren_active = False

def trigger_relay():
    global _relay_active
    _relay_active = True
    yellow.on()
    relay.on()
    time.sleep(RELAY_DURATION)
    relay.off()
    yellow.off()
    time.sleep(1)
    _relay_active = False

def indicate_motion():
    if not _siren_active:
        yellow.blink(on_time=0.1, off_time=0.1, n=3, background=True)

def update_gate_leds(is_open):
    if _siren_active: return

    if is_open:
        green.off()
        red.on()
    else:
        red.off()
        green.on()

if gate_switch.is_pressed:
    green.on()
else:
    red.on()
