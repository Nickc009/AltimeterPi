# AltimeterPi
Raspberry Pi and SenseHat Altimeter Project
#### Video Demo:  <URL HERE>
#### Description:
This project implements a data logging and visualization system using a Raspberry Pi with a Sense HAT sensor board.
The application is built with Flask, a web framework for Python, and it provides a real-time web interface to monitor temperature, humidity, and altitude data.
The sensor readings are logged to a CSV file, and a live graph is displayed on a web page using Server-Sent Events (SSE).

Files:
app.py: This is the main script containing the Flask application.
It initializes the Sense HAT, logs sensor data, updates a live graph, and handles graceful shutdowns.
The script also includes a threaded timer to periodically log data.
templates/index.html: This HTML file defines the main landing page for the web application.
It can be customized to include additional information or features.
templates/live_graph.html: This HTML file is responsible for rendering the live graph on a separate web page.
It includes placeholders for the dynamically updated graph image.
static/live_graph.png: This is the image created after every data cycle of the most current data.
altimeterboot.service: This file needs to be placed in /etc/systemd/system/
its responsible for the autostart at boot functionallity of the app.

Usage:
Installation: Ensure that the required Python libraries are installed.
You can install them using pip install -r requirements.txt.
The Sense HAT library and other dependencies are specified in this file.
Ensure that
Execution: Simply plug device into powersource.
Live Graph: Navigate to the "Live Graph" page to view real-time updates of temperature, humidity, and altitude data. The graph is automatically updated at regular intervals.

Design Choices:
Threaded Data Logging: The project uses a threaded approach to log sensor data at regular intervals. This ensures that the Flask web server can run concurrently with the data logging process.
Dynamic Plotting: Matplotlib is used for dynamic plotting of temperature, humidity, and altitude data. The live graph is updated on-the-fly without the need for manual page refreshes.
Server-Sent Events (SSE): SSE is employed to enable real-time updates on the web page.
This allows for a continuous stream of data from the server to the client, providing a smooth and efficient user experience.
Graceful Shutdown: The application includes a signal handler to perform a graceful shutdown when the user presses Ctrl+C or sends a termination signal.
This ensures proper cleanup of resources, including stopping the Sense HAT and the threaded data logging.

Contributions and Future Enhancements:
Contributions to this project are welcome.
Some potential enhancements include additional sensor support, a more interactive web interface, and improved error handling.
Feel free to open issues for bugs or feature requests!
