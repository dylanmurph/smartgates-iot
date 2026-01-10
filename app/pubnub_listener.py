import time
from pubnub.callbacks import SubscribeCallback
from app import db, create_app
from app.models import Device, EventLog
from app.hardware_service import pubnub

def start_listening():
    app = create_app()
    
    with app.app_context():
        class DatabaseListener(SubscribeCallback):
            def message(self, pubnub, message):
                if message.publisher == "aws_server":
                    return

                data = message.message
                channel_name = message.channel
                
                try:
                    device_id = int(channel_name)
                    device = Device.query.get(device_id)

                    if device:
                        new_log = EventLog(
                            event_type=data,
                            description=f"Hardware Event: {data}",
                            device_id=device.id,
                        )
                        db.session.add(new_log)
                        db.session.commit()
                        print(f"Logged {data} for Device ID: {device_id}")
                except Exception as e:
                    db.session.rollback()
                    print(f"Listener Error: {e}")

        pubnub.add_listener(DatabaseListener())
        pubnub.subscribe().channels("1").execute()
        
        print("--- PUBNUB LISTENER THREAD STARTED ---")
        
        while True:
            time.sleep(1)