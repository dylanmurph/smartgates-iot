import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from app import Device

pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.environ.get("PUBNUB_SUBSCRIBE_KEY")
pnconfig.publish_key = os.environ.get("PUBNUB_PUBLISH_KEY")
pnconfig.user_id = os.environ.get("PUBNUB_USER_ID", "aws_server")
pubnub = PubNub(pnconfig)


def trigger_gate(device_id):
    device = Device.query.get(device_id)
    if not device or not device.unique_id:
        return False, "Device unique_id not found"

    try:
        # We now publish to the unique_id (e.g., "gate_pi_01") 
        # instead of the database primary key ("1")
        channel_name = str(device.unique_id)
        pubnub.publish().channel(channel_name).message("OPEN_GATE").sync()
        return True, f"Signal sent to {channel_name}"
    except Exception as e:
        return False, str(e)
