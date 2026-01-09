import os
from dotenv import load_dotenv
from app import create_app
from app.hardware_service import start_hardware_service

load_dotenv()

app = create_app()

try:
    start_hardware_service(app)
except Exception as e:
    print(f"Hardware start warning: {e}")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)