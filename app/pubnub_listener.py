import time
import os
from pubnub.callbacks import SubscribeCallback
from app import create_app, db
from app.models import Device, EventLog
from app.hardware_service import pubnub

app = create_app()

class DatabaseListener(SubscribeCallback):
    def message(self, pubnub, message):
        # Ignore messages sent by the server itself
        if message.publisher == "aws_server":
            return

        data = message.message
        channel_name = message.channel

        description_map = {
            "MOTION_DETECTED":     "Motion detected at gate - Panel open",
            "TAMPER_ALARM":        "Tamper - Device lid open",
            "TAMPER_CLEARED":      "Tamper - Device lid closed",
            "GATE_OPEN":           "Gates are open",
            "GATE_CLOSED":         "Gates are closed",
            "GATE_CYCLE_COMPLETE": "Success - Gate triggered successfully"
        }

        final_description = description_map.get(data, data)

        with app.app_context():
            try:
                device_id = int(channel_name)
                device = Device.query.get(device_id)

                if device:
                    # --- UPDATE DEVICE STATUS BOOLEANS ---
                    if data == "GATE_OPEN":
                        device.is_gate_open = True
                    elif data == "GATE_CLOSED":
                        device.is_gate_open = False
                    elif data == "TAMPER_ALARM":
                        device.is_tamper_active = True
                    elif data == "TAMPER_CLEARED":
                        device.is_tamper_active = False

                    # --- CREATE EVENT LOG ---
                    new_log = EventLog(
                        event_type=data,
                        description=final_description,
                        device_id=device.id,
                    )

                    db.session.add(new_log)
                    db.session.commit()
                    print(f"Logged {final_description} and updated status for Device ID: {device_id}")
                else:
                    print(f"Device with ID {device_id} not found in database.")

            except Exception as e:
                db.session.rollback()
                print(f"Listener Error: {e}")

def start_listening():
    
    # Attach our custom listener
    pubnub.add_listener(DatabaseListener())
    
    # Subscribe to your channel (Device ID "1")
    pubnub.subscribe().channels("1").execute()
    
    print("--- PUBNUB LISTENER ONLINE ---")
    print("Watching for Hardware Events...")

    # Keep the script alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping Listener...")

if __name__ == "__main__":
    start_listening()