import os
import threading
from dotenv import load_dotenv
from app import create_app
from app.pubnub_listener import start_listening 

load_dotenv()

app = create_app()

if __name__ == '__main__':
    listener_thread = threading.Thread(target=start_listening, daemon=True)
    listener_thread.start()
    app.run(debug=True, use_reloader=False)