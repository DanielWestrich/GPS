import csv
import time
import math
import codecs
import serial
import gmplot
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

LORA_PORT = '/dev/cu.SLAB_USBtoUART'
BAUD_RATE = 9600
PLOT_RATE = 1
FEET_PER_METER = 3.28084
FEET_PER_DECIMAL_DEGREE = 69 * 5280
FEET_PER_SECOND_TO_MILES_PER_HOUR = 3600 / 5280

def main_func(file_writer, counter, prev_values, driver):
    arduino = serial.Serial(LORA_PORT, BAUD_RATE)
    # arduino.flushInput()
    # arduino.flushOutput()
    time.sleep(2)
    arduino_data = arduino.readline()[:-2].decode("utf-8")
    list_values = str(arduino_data[0:len(arduino_data)]).split(':')

    #  list_values = [0,0,0,0,0,0,0]  # Use for testing

    dict_values = {
        "timestamp" : datetime.now(),
        "lat" : float(list_values[0]),
        "lng" : float(list_values[1]),
        "alt" : int(float(list_values[2]) * FEET_PER_METER),
        "speed" : 0,
        "sat" : int(list_values[3]),
        "rssi" : int(list_values[4])
    }

    if counter > 1:
        dict_values['speed'] = calc_speed(dict_values, prev_values)
    else:
        dict_values['speed'] = 0

    print(dict_values)
    save_results(dict_values, file_writer)

    if counter % PLOT_RATE == 0:
        show_map(dict_values, driver)

    arduino_data = 0
    arduino.close()
    return dict_values
    print('<----------------------------->')

def calc_speed(values, prev_values):
    distance = float(math.sqrt(
                math.pow((values['lat'] - prev_values['lat']) * FEET_PER_DECIMAL_DEGREE, 2) +
                math.pow((values['lng'] - prev_values['lng']) * FEET_PER_DECIMAL_DEGREE, 2) +
                math.pow(values['alt'] - prev_values['alt'], 2)))
    time = float((values['timestamp'] - prev_values['timestamp']).total_seconds())
    speed = float(distance / time) * FEET_PER_SECOND_TO_MILES_PER_HOUR
    print("Distance (ft): ", distance)
    print("Time (s): ", time)
    print("Speed (mph): ", speed)
    return speed

def save_results(values, file_writer):
    file_writer.writerow(values.values())

def show_map(values, driver):
    print("Displaying Coordinates on Map")

    latitude_list.append(values['lat'])
    longitude_list.append(values['lng'])
      
    gmap = gmplot.GoogleMapPlotter(values['lat'], values['lng'], 17) 
    gmap.scatter([values['lat']], [values['lng']], '#FF0000', size = 2, marker = False)
    gmap.plot([values['lat']], [values['lng']], 'cornflowerblue', edge_width = 2.5)
    gmap.draw('index.html')
    driver.refresh()
    print("Updated Map")
    time.sleep(0.25)
    ok_btn = driver.find_element_by_xpath('//*[@id="map_canvas"]/div[2]/table/tr/td[2]/button')
    ok_btn.click()


# ----------------------------------------Main Code------------------------------------
# Declare variables to be used

latitude_list = []
longitude_list = []

now = str(datetime.now())
file_name = "/Users/Djwestrich/Desktop/programs/raspberrypi/gps/gps_received_data/" + now + ".csv"
with open(file_name, 'w') as ofile:
    writer = csv.writer(ofile)
    writer.writerow(['timestamp', 'lat', 'lng', 'alt', 'speed', 'sat', 'rssi'])

    print('Program started')

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('file:///Users/Djwestrich/Desktop/programs/raspberrypi/gps/index.html')
    print("Opened Map")

    prev_values = {}
    counter = 1
    while True:
        try:
            prev_values = main_func(writer, counter, prev_values)
        except Exception as e:
            print("Error: ", e)
            pass
        counter += 1
