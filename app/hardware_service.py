import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.environ.get("PUBNUB_SUBSCRIBE_KEY")
pnconfig.publish_key = os.environ.get("PUBNUB_PUBLISH_KEY")
pnconfig.user_id = os.environ.get("PUBNUB_USER_ID", "aws_server")
pubnub = PubNub(pnconfig)

def trigger_gate():
    try:
        pubnub.publish().channel("gate_channel").message("OPEN_GATE").sync()
        return True, "Signal Sent"
    except Exception as e:
        return False, str(e)