import csv
import time
import math
import gmaps
import serial
import gmplot
import requests
# import schedule
from datetime import datetime
# from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

LORA_PORT = '/dev/cu.SLAB_USBtoUART'
# URL = 'http://localhost:5000/'
BAUD_RATE = 9600
PLOT_RATE = 1
FEET_PER_METER = 3.28084

def main_func(file_writer, counter, prev_values):
    arduino = serial.Serial(LORA_PORT, BAUD_RATE)
    # arduino.flushInput()
    # arduino.flushOutput()
    time.sleep(2)
    # print('Established serial connection to LoRa module')
    arduino_data = arduino.readline()[:-2].decode("utf-8")
    # print("Arduino Data: ", arduino_data)
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
    # print('Connection closed')
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
# marker_locations = []

now = str(datetime.now(tz=None))
file_name = "/Users/Djwestrich/Desktop/programs/raspberrypi/gps/gps_received_data/" + now + ".csv"
with open(file_name, 'w') as ofile:
    writer = csv.writer(ofile, delimiter='\t')
    writer.writerow(['timestamp', 'lat', 'lng', 'alt', 'sat', 'rssi'])

    print('Program started')

    # Setting up the Arduino
    # schedule.every(1).seconds.do(main_func)

    prev_values = {}
    counter = 1
    while True:
        # schedule.run_pending()
        try:
            prev_values = main_func(writer, counter, prev_values)
        except Exception as e:
            print("Error: ", e)
            pass
        # time.sleep(1)
        counter += 1

