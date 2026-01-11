import os
import time
from dotenv import load_dotenv
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import hardware

load_dotenv()

# --- PUBNUB SETUP ---
pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pnconfig.user_id = os.getenv("PUBNUB_USER_ID", "pi_hub")
pubnub = PubNub(pnconfig)

DEVICE_ID = "1"

# --- STATE TRACKING ---
tamper_active = False
gate_is_open = False

def publish_log(msg):
    print(f"PUB: {msg}")
    pubnub.publish().channel(DEVICE_ID).message(msg).sync()

def on_motion():
    print("Motion Detected")
    hardware.indicate_motion()
    publish_log("MOTION_DETECTED")

def on_tamper():
    global tamper_active
    if not tamper_active:
        tamper_active = True
        print("Tamper Alarm")
        publish_log("TAMPER_ALARM")
        hardware.start_siren()

def on_tamper_clear():
    global tamper_active
    if tamper_active:
        tamper_active = False
        print("Tamper Cleared")
        publish_log("TAMPER_CLEARED")
        hardware.stop_siren()

def on_gate_open():
    global gate_is_open
    if not gate_is_open:
        gate_is_open = True
        print("Gate Open")
        hardware.update_gate_leds(is_open=True)
        publish_log("GATE_OPEN")

def on_gate_close():
    global gate_is_open
    if gate_is_open:
        gate_is_open = False
        print("Gate Closed")
        hardware.update_gate_leds(is_open=False)
        publish_log("GATE_CLOSED")

# --- CONNECT LOGIC TO HARDWARE ---
hardware.pir.when_motion = on_motion
hardware.ldr.when_activated = on_tamper
hardware.ldr.when_deactivated = on_tamper_clear
hardware.gate_switch.when_released = on_gate_open
hardware.gate_switch.when_pressed = on_gate_close

# --- LISTENER FOR INCOMING COMMANDS ---
class GateListener(SubscribeCallback):
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            print(f"SYSTEM ONLINE: Connected as {pnconfig.user_id}")

    def message(self, pubnub, message):
        data = message.message
        print(f"CMD: {data}")

        if data == "OPEN_GATE":
            print("Triggering Relay...")
            hardware.trigger_relay()
            publish_log("GATE_CYCLE_COMPLETE")

    def presence(self, pubnub, presence): pass

pubnub.add_listener(GateListener())
pubnub.subscribe().channels(DEVICE_ID).execute()

print("Security System Running.")
print("Press CTRL+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
    hardware.stop_siren()
