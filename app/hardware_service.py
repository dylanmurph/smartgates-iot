import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.environ.get("PUBNUB_SUBSCRIBE_KEY")
pnconfig.publish_key = os.environ.get("PUBNUB_PUBLISH_KEY")
pnconfig.user_id = os.environ.get("PUBNUB_USER_ID", "aws_server")
pubnub = PubNub(pnconfig)

def trigger_gate(device_id):
    try:
        channel_name = f"gate_{device_id}" 
        pubnub.publish().channel(channel_name).message("OPEN_GATE").sync()
        return True, f"Signal Sent to {channel_name}"
    except Exception as e:
        return False, str(e)