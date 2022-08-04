import argparse
import requests
from datetime import datetime
import json
import os
import csv
import pytz
from pathlib import Path
import re


# paths
CURRENT_PATH = Path(__file__).parent.resolve()

# default output filename
DEFAULT_FILENAME = 'outputs.csv'

# endpoints
BACKEND_ENDPOINT = "https://pi-backend-api.herokuapp.com/pi"

# file headers
CSV_HEADERS = ["Date Run", "Date Input", "Sea Level Pressure (mb)", "Ocean Temperature Profile", "Average Ocean Temperature", "Potential Maximum Wind Velocity (m/s)", "Minimum Pressure At Eye (mb)", "Outflow Temperature (K)", "Ocean Temperature Source",
               "Earliest Ocean Recording", "Latest Ocean Recording", "Earliest Atmospheric Recording", "Latest Atmospheric Recording", "Full log"]

# parameter contraints
MINIMUM_LAYER_DEPTH = 15

# SYSTEM ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument("-d", type=int, dest='date_digits',
                    help="Date and time (format YYYYMMDDHH)")
parser.add_argument("-t", type=str, dest='ocean_profile',
                    help="""Ocean sample depth 'tX' where X is layer depth or 'sst' """)
parser.add_argument("-p", type=float, dest='slp',
                    help="Sea level Pressure (mb)", required=True)
parser.add_argument("-o", type=str, dest='output_path', help="Output path")
args = parser.parse_args()


# halts program execution if a bad input is given in the system arguments
def argument_error(bad_arguments):
    for argument in bad_arguments:
        print(str(argument) + " is not valid")
        exit()


# validates date attributes are correct
def validate_date(year, month, day, hour):
    try:
        dt = datetime(year, month, day, hour)
        return True
    except ValueError:
        return False


# checks date is not in the future
def check_date(datetime):
    if datetime > datetime.now():
        print("Date cannot be in the future")
        return False
    else:
        return True


# returns datetime object from string format YYYYMMDDHH
def get_datetime_from_digits(digits):
    str_digits = str(digits)
    year = int(str_digits[0:4])
    month = int(str_digits[4:6])
    day = int(str_digits[6:8])
    hour = int(str_digits[8:10])
    if validate_date(year, month, day, hour) == True:
        dt = datetime(year, month, day, hour)
        if check_date(dt) == True:
            return dt
        else:
            argument_error([dt])
    else:
        argument_error([str_digits])


# returns ocean layer depth from aregument - sst returns 0, tX returns X as number
def get_ocean_profile_depth(raw_input):
    input_profile = str(raw_input).lower()
    if(input_profile == "sst"):
        return 0
    elif(re.match(r"t[0-9]+", input_profile)):
        try:
            profile = float(input_profile.split("t")[1])
            return profile if profile > 0 else argument_error([raw_input])
        except:
            argument_error([raw_input])
    else:
        argument_error([raw_input])


# checks sea level pressure > 0
def check_slp(slp):
    if slp > 0:
        return True
    else:
        return False


# validates sea level pressure
def get_slp(input_slp):
    if check_slp(input_slp) == True:
        return input_slp
    else:
        argument_error([input_slp])


# creates directory if not exists
def carve_path(path):
    if not os.path.exists(path.parent):
        os.makedirs(path.parent)


# saves array of outputs to csv file at given path
# if file does not exist at path, one is created
def save_to_csv(path, data):
    print("Saving outputs to CSV file {}".format(path))
    carve_path(path)
    if os.path.isfile(path) == True:
        with open(path) as csv_file:
            row_count = sum(1 for line in csv_file)
            if row_count == 0:
                with open(path, 'w', encoding='UTF8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(CSV_HEADERS)
                    writer.writerow(data)
            else:
                with open(path, 'a', encoding='UTF8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(data)
    else:
        with open(path, 'w', encoding='UTF8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CSV_HEADERS)
            writer.writerow(data)
    return None


# saves JSON object to JSON file at given path
def save_to_json(path, data):
    carve_path(path)
    with open(path, 'w') as json_file:
        print("Saving full log to JSON file {}".format(path))
        json.dump(data, json_file, indent=4)
    return None


# INPUT VARIABLES
# datetime - if omitted, uses current date and time (UTC)
requested_datetime = get_datetime_from_digits(
    args.date_digits) if args.date_digits is not None else datetime.now(tz=pytz.timezone("UTC"))

# ocean profile - if omitted, uses top 50m layer
ocean_profile = get_ocean_profile_depth(
    args.ocean_profile) if args.ocean_profile is not None else 50

# sea level pressure
SLP = get_slp(args.slp)

# output path - if omitted, uses outputs.csv at current directory
output_path = Path(
    args.output_path) if args.output_path is not None else CURRENT_PATH.joinpath(DEFAULT_FILENAME)

# path to full log file
log_path = output_path.parent.joinpath('logs').joinpath(
    "{}.json".format(datetime.now(tz=pytz.timezone('UTC')).strftime("%Y-%m-%dT%H%M%S")))

# url parameters
params = {
    "datetime": requested_datetime.isoformat(), "seaLevelPressure": SLP, "oceanLayerDepth": ocean_profile if ocean_profile > 0 else MINIMUM_LAYER_DEPTH, "sstFlag": True if ocean_profile == 0 else False}

# makes GET request to backend, and returns response
print("""Requesting data and predictions from PI REST API for:
Date: {}
Sea level pressure: {}
Using:
{}
""".format(params["datetime"], params["seaLevelPressure"], "TOP {}m layer".format(ocean_profile)
           if ocean_profile > 0 else "SST"))

response = requests.get(BACKEND_ENDPOINT, params=params)

# loads data from JSON response and generates array of outputs for csv file
if(response.status_code == 200):
    print("Success")
    data = json.loads(response.content)

    # appends outputs to array, representing each column in output CSV file
    csv_data = []
    csv_data.append(datetime.now(tz=pytz.timezone(
        'UTC')).strftime("%Y-%m-%d %H:%M:%S"))
    csv_data.append(requested_datetime.strftime("%Y-%m-%d %H:%M:%S"))
    csv_data.append(SLP)
    csv_data.append("TOP {}m layer".format(ocean_profile)
                    if ocean_profile > 0 else "SST")
    csv_data.append(data['dataSources']['ocean']
                    ['metadata']['averageTemperatureUsed'])
    csv_data.append(data['predictions']['data']['maximumWindSpeed'])
    csv_data.append(data['predictions']['data']['minimumCentralPressure'])
    csv_data.append(data['predictions']['data']['outflowTemperature'])
    csv_data.append(data['dataSources']['ocean']['metadata']['sourceName'])
    csv_data.append(data['dataSources']['ocean']
                    ['metadata']['timeframe']['start'])
    csv_data.append(data['dataSources']['ocean']
                    ['metadata']['timeframe']['end'])
    csv_data.append(data['dataSources']['atmosphere']
                    ['metadata']['timeframe']['start'])
    csv_data.append(data['dataSources']['atmosphere']
                    ['metadata']['timeframe']['end'])
    csv_data.append(log_path)

    # if calculations ran successfully, save outputs to csv file
    if data['predictions']['metadata']['outcome'] == "Successful":
        save_to_csv(output_path, csv_data)
        save_to_json(log_path, data)
else:
    # print error code
    print("Error {}".format(response.status_code))
