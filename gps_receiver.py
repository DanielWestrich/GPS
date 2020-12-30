import csv
import time
import math
import serial
import gmplot
from datetime import datetime

LORA_PORT = '/dev/cu.SLAB_USBtoUART'
BAUD_RATE = 9600
PLOT_RATE = 1  # Used to define how frequently to plot map location. 1 in PLOT_RATE iterations of the loop
FEET_PER_METER = 3.28084
FILE_PATH = ""  # Insert your local file path here. Each file will be named using the current timestamp

def main_func(file_writer, counter, prev_values):
    arduino = serial.Serial(LORA_PORT, BAUD_RATE)
    time.sleep(2)  # Wait to buffer the next packet before reading. This timing is arbitrary, so anticipate occasional errors.
    arduino_data = arduino.readline()[:-2].decode("utf-8")  # Decode the packet into readable text
    list_values = str(arduino_data[0:len(arduino_data)]).split(':')

    dict_values = {
        "timestamp" : str(datetime.now(tz=None)),
        "lat" : float(list_values[0]),
        "lng" : float(list_values[1]),
        "alt" : int(float(list_values[2]) * FEET_PER_METER),
        "speed" : int(0)
        "sat" : int(list_values[3]),
        "rssi" : int(list_values[4])
    }

    if counter > 1:
        speed = calc_speed(dict_values, prev_values)
    else:
        speed = 0

    dict_values['speed'] = speed

    print(dict_values)
    save_results(dict_values, file_writer)

    if counter % PLOT_RATE == 0:
        show_map(dict_values)

    arduino_data = 0
    arduino.close()
    return dict_values
    print('<----------------------------->')

def calc_speed(values, prev_values):
    distance = float(math.sqrt(math.pow(values['lat'] - prev_values['lat'], 2) +
                math.pow(values['lng'] - prev_values['lng'], 2) +
                math.pow(values['alt'] - prev_values['alt'], 2) * 1.0))
    time = float(values['timestamp'] - prev_values['timestamp'])
    return int(distance / time)

def save_results(values, file_writer):
    file_writer.writerow(values.values())

@csrf_exempt
def show_map(values):
    print("Displaying Coordinates on Map")

    latitude_list.append(values['lat'])
    longitude_list.append(values['lng'])
      
    # For the below, uncomment the two lines and comment the corresponding two lines if you'd like to plot all locations at once. Leave as-is if you'd only like to plot the current location
    gmap = gmplot.GoogleMapPlotter(values['lat'], values['lng'], 17) 
    # gmap.scatter(latitude_list, longitude_list, '#FF0000', size = 5, marker = False)
    gmap.scatter([values['lat']], [values['lng']], '#FF0000', size = 2, marker = False)
    # gmap.plot(latitude_list, longitude_list, 'cornflowerblue', edge_width = 2.5)
    gmap.plot([values['lat']], [values['lng']], 'cornflowerblue', edge_width = 2.5)
    gmap.draw('index.html')


# ----------------------------------------Main Code------------------------------------
# Declare variables to be used

latitude_list = []
longitude_list = []

now = str(datetime.now(tz=None))
file_name = FILE_PATH + now + ".csv"
with open(file_name, 'w') as ofile:
    writer = csv.writer(ofile, delimiter='\t')
    writer.writerow(['timestamp', 'lat', 'lng', 'alt', 'sat', 'rssi'])

    print('Program started')

    prev_values = {}
    counter = 1
    while True:
        try:
            prev_values = main_func(writer, counter, prev_values)
        except Exception as e:
            print("Error: ", e)
            pass
        counter += 1

