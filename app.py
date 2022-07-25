from app import app, scheduler
import threading
from app.route.routes import get_values_from_serial

get_serial_data = threading.Thread(target = get_values_from_serial)
if __name__ == '__main__':
    print("hello,threading")
    get_serial_data.start()
    scheduler.start()
    app.run(debug=True,host='0.0.0.0')