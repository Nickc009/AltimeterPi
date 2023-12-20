from flask import Flask, render_template, Response
from threading import Thread, Event
from sense_hat import SenseHat
from datetime import datetime
from time import sleep
import signal
import sys
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

FILENAME = ""
TEMPERATURE = True
HUMIDITY = True
PRESSURE = True
DELAY = 5

temp_offset = -17.2  # in F
humidity_offset = 8.5  # in %
pressure_offset = -65  # in Feet

sense = SenseHat()

# Initialize data variables
temperature_data = []
humidity_data = []
altitude_data = []
time_data = []

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

class TimedLogThread(Thread):
    def __init__(self, stop_event):
        super().__init__()
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            log_data()
            update_plot()
            sleep(DELAY)

def file_setup(FILENAME):
    header = ["temperature", "humidity", "altitude", "time"]

    with open(FILENAME, "w") as f:
        f.write(",".join(str(value) for value in header) + "\n")

def calculate_altitude(pressure):
    sea_level_pressure = 1013.25
    altitude = 44330.8 * (1 - (pressure / sea_level_pressure) ** 0.1903)
    return altitude * 3.28084 + pressure_offset

def get_sense_data():
    sense_data = []

    if TEMPERATURE:
        sense_data.append(sense.get_temperature())
    if HUMIDITY:
        sense_data.append(sense.get_humidity())
    if PRESSURE:
        sense_data.append(sense.get_pressure())

    sense_data.append(datetime.now())
    return sense_data

def log_data():
    sense_data = get_sense_data()
    calibrated_temperature = sense_data[0] * 9 / 5 + 32 + temp_offset
    calibrated_humidity = sense_data[1] + humidity_offset
    calibrated_altitude = calculate_altitude(sense_data[2]) + pressure_offset

    # Update sense_data with calibrated values
    sense_data[0] = calibrated_temperature
    sense_data[1] = calibrated_humidity
    sense_data[2] = calibrated_altitude

    # Update data for the graph
    temperature_data.append(sense_data[0])
    humidity_data.append(sense_data[1])
    altitude_data.append(sense_data[2])
    time_data.append(sense_data[3])

    # Create a comma-separated string and put it into the batch_data queue
    output_string = ",".join(str(value) for value in sense_data)

    # Debug print statement
    print("Debug - Output String:", output_string)

    # Write data to the file immediately
    with open(FILENAME, "a") as f:
        f.write(output_string + "\n")

def update_plot():
    ax1.clear()
    ax2.clear()

    # Temp and Humidity plotting
    ax1.plot(time_data[1:], temperature_data[1:], label="Temperature")
    ax1.plot(time_data[1:], humidity_data[1:], label="Humidity")
    ax1.set_ylabel('Temperature and Humidity ~F %rH')
    ax1.legend()

    ax2.plot(time_data[1:], altitude_data[1:], label="Altitude")
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Altitude ~feet')
    ax2.legend()

    plt.suptitle('Live Sensor Data')

    plt.savefig('static/live_graph.png')

def cleanup(signum, frame):
    print("Cleaning up...")
    sense.clear()

    # Signal the thread to stop
    stop_event.set()

    # Wait for the thread to finish
    if 'timed_log_thread' in locals():
        timed_log_thread.join()

    print("Flask app shutting down gracefully.")
    sys.exit(0)

# Register the signal handler for a graceful shutdown
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGTSTP, cleanup)  # Handle Ctrl + Z

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def generate_data():
    def generate():
        while True:
            latest_line = get_latest_line()
            yield f"data:{latest_line}\n\n"
            sleep(DELAY)

    return Response(generate(), content_type="text/event-stream")

@app.route("/live-graph")
def live_graph():
    return render_template("live_graph.html")

def get_latest_line():
    with open(FILENAME, "r") as f:
        lines = f.readlines()
        if lines:
            return lines[-1].strip()
        else:
            return ""

if __name__ == "__main__":
    timestamp = str(datetime.now())
    if FILENAME == "":
        FILENAME = "SenseLog-" + str(datetime.now()) + ".csv"
    else:
        FILENAME = FILENAME + "-" + str(datetime.now()) + ".csv"

    file_setup(FILENAME)

    # Create an instance of the Event
    stop_event = Event()

    if DELAY > 0:
        # Create an instance of the TimedLogThread and pass the stop_event
        timed_log_thread = TimedLogThread(stop_event)
        timed_log_thread.start()

    # Use threaded=True to run Flask in a threaded mode
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

    # After Flask app exits, stop the thread
    stop_event.set()
    timed_log_thread.join()
