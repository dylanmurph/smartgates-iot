from app import create_app
from app.hardware_service import start_hardware_service

app = create_app()

if __name__ == '__main__':
    start_hardware_service(app)

    app.run(debug=True, use_reloader=False)