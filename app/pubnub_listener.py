import time
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from app import create_app, db
from app.models import Device, EventLog
from app.hardware_service import pubnub


class DatabaseListener(SubscribeCallback):
    def message(self, pubnub, message):
        data = message.message
        channel_name = message.channel

        app = create_app()
        with app.app_context():
            try:
                device_id = int(channel_name)
                device = Device.query.get(device_id)

                if device:
                    new_log = EventLog(
                        event_type=data,
                        description=f"Log from Pi {device_id}",
                        device_id=device.id,
                    )
                    db.session.add(new_log)
                    db.session.commit()
                    print(f"Logged {data} for Device ID: {device_id}")
            except ValueError:
                print(f"Received message on non-numeric channel: {channel_name}")


if __name__ == "__main__":
    pubnub.add_listener(DatabaseListener())

    pubnub.subscribe().channels("gate_channel").execute()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Listener...")
