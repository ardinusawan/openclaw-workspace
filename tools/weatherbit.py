#!/usr/bin/env python3
"""
Weatherbit.io API helper for OpenClaw
Reads API key from ~/.openclaw/.env
"""

import os
import sys
import urllib.request
import json

# Load API key from .env
env_file = os.path.expanduser("~/.openclaw/.env")
weatherbit_key = None

try:
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('WEATHERBIT_API_KEY='):
                weatherbit_key = line.split('=', 1)[1].strip()
                break
except FileNotFoundError:
    print("Error: .env file not found at ~/.openclaw/.env")
    sys.exit(1)

if not weatherbit_key or weatherbit_key == 'your_weatherbit_api_key_here':
    print("Error: WEATHERBIT_API_KEY not set in .env file")
    sys.exit(1)

# Parse command line arguments
if len(sys.argv) < 3:
    print("Usage: python3 weatherbit.py <lat> <lon> [--units C|F]")
    sys.exit(1)

lat = sys.argv[1]
lon = sys.argv[2]
units = 'C'  # Default

if len(sys.argv) > 3:
    if sys.argv[3] in ['C', 'F', 'M', 'I']:
        units = sys.argv[3]

# Weatherbit API units mapping
# C = Celsius, F = Fahrenheit, M = Metric, I = Imperial
unit_param = 'metric' if units in ['C', 'M'] else 'imperial'

# Make API request
url = f"https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={weatherbit_key}&units={unit_param}"

try:
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'OpenClaw/1.0')
    request.add_header('Accept', 'application/json')

    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode())

    if 'error' in data:
        print(f"API Error: {data['error']}")
        sys.exit(1)

    weather = data['data'][0]

    # Display weather info
    print(f"Weather for {weather['city_name']}, {weather['country_code']}")
    print(f"Temperature: {weather['temp']}°{'C' if unit_param == 'metric' else 'F'}")
    print(f"Feels Like: {weather['app_temp']}°{'C' if unit_param == 'metric' else 'F'}")
    print(f"Condition: {weather['weather']['description']}")
    print(f"Humidity: {weather['rh']}%")
    print(f"Wind: {weather['wind_spd']} km/h from {weather['wind_cdir_full']}")
    print(f"Pressure: {weather['pres']} hPa")
    print(f"UV Index: {weather['uv']}")
    print(f"Last Updated: {weather['ob_time']}")

except urllib.error.URLError as e:
    print(f"Network Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
