
import os
import time
from dotenv import load_dotenv
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from gpiozero import OutputDevice

relay = OutputDevice(17, active_high=True, initial_value=False)

load_dotenv()

pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pnconfig.user_id = os.getenv("PUBNUB_USER_ID")
pubnub = PubNub(pnconfig)

class GateListener(SubscribeCallback):
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            print("Connected to PubNub Successfully")

    def message(self, pubnub, message):
        data = message.message
        print(f"Message Received: {data}")

        if data == "OPEN_GATE":
            print("Relay ON")
            relay.on()
            time.sleep(5)
            relay.off()
            print("Relay OFF")

    def presence(self, pubnub, presence):
        pass

pubnub.add_listener(GateListener())
pubnub.subscribe().channels("gate_channel").execute()

print("Initializing Gate Listener...")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("System Stopping...")
