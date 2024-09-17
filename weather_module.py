from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
import requests
import socket
from urllib.parse import quote_plus
from historical_weather_date import function_call

weather_blueprint = Blueprint('weather', __name__)


def constructApiUrl(days, location, parameters, format='json'):
    base_url = "https://api.meteomatics.com"
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=days)
    formatted_start_date = start_date.strftime("%Y-%m-%dT00:00:00Z")
    formatted_end_date = end_date.strftime("%Y-%m-%dT00:00:00Z")
    return f"{base_url}/{formatted_start_date}--{formatted_end_date}:PT1H/{parameters}/{location}/{format}"


def constructLocationApiUrl(address):
    base_url = "https://geocode.maps.co/search"
    api_key = "669331b0ea8b7684602117lgyf7be29"
    encoded_address = quote_plus(address)
    print(f"{base_url}?q={encoded_address}&api_key={api_key}")
    return f"{base_url}?q={encoded_address}&api_key={api_key}"


def constructTimeZoneApiUrl(lat, lon, timestamp):
    base_url = "https://maps.googleapis.com/maps/api/timezone/json"
    api_key = "AIzaSyBQtYCOO5-pVAJ9Q-800s3hs5LwKLfIum0"
    return f"{base_url}?location={lat},{lon}&timestamp={timestamp}&key={api_key}"


def fetchWeatherData(days, location, parameters):
    username = "none_sato_hokuto-daniel"
    password = "7M8Q2Vyut2"
    format = "json"

    apiurl = constructApiUrl(days, location, parameters, format)
    print(f"Constructed API URL: {apiurl}")  # Debug print to check the URL

    # Check DNS resolution
    try:
        print(f"Resolving DNS for api.meteomatics.com: {socket.gethostbyname('api.meteomatics.com')}")
    except socket.error as err:
        print(f"DNS resolution error: {err}")

    try:
        response = requests.get(apiurl, auth=(username, password))
        print(f"API Response Status: {response.status_code}")  # Debug print to check response status
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def fetch_coordinates(address):
    apiUrl = constructLocationApiUrl(address)
    try:
        response = requests.get(apiUrl)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            function_call(lat, lon)
            return f"{lat},{lon}"
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None


def convert_UTC_to_LocalTime(utc_time, utc_offset):
    return utc_time + timedelta(seconds=utc_offset)


def fetch_date(lat, lon, timestamp):
    apiUrl = constructTimeZoneApiUrl(lat, lon, timestamp)
    try:
        response = requests.get(apiUrl)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching timezone data: {e}")
        return None


@weather_blueprint.route('/weather')
def weather():
    days = 7
    location = "33.7175,-117.8311"
    parameters = "t_2m:C"

    weather_data = fetchWeatherData(days, location, parameters)
    print(f"Fetched weather data: {weather_data}")  # Debug print to check the fetched data
    if weather_data:
        return render_template('index.html', weather_data=weather_data)
    else:
        return {"Error": "No data available"}


@weather_blueprint.route('/get_location', methods=['GET'])
def get_location():
    address = request.args.get('address')
    if address:
        print(f"Received address: {address}")
        coordinates = fetch_coordinates(address)
        if coordinates:
            print(f"Fetched coordinates: {coordinates}")
            latitude, longitude = coordinates.split(',')
            timestamp = int(datetime.utcnow().timestamp())

            timezone_data = fetch_date(latitude, longitude, timestamp)
            if timezone_data:
                print(f"Fetched timezone data: {timezone_data}")
                utc_offset = timezone_data['rawOffset'] + timezone_data['dstOffset']
                print(f"Fetched timezone offset: {utc_offset}")
                local_time = convert_UTC_to_LocalTime(datetime.utcnow(), utc_offset)
                response_data = {
                    "local_time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "timezone_name": timezone_data['timeZoneName'],
                    "utc_offset": utc_offset,
                    "lat": latitude, "lon": longitude
                }
                days = 7
                parameters = "t_2m:C,weather_symbol_1h:idx,t_max_2m_24h:C,t_min_2m_24h:C"
                weather_data = fetchWeatherData(days, coordinates, parameters)
                if weather_data:
                    return jsonify(
                        {
                            "weather_data": weather_data,
                            "local_time": response_data['local_time'],
                            "utc_offset": response_data['utc_offset'],
                            "lat": latitude,
                            "lon": longitude
                        }
                    )
                else:
                    print("Error: Weather data not found.")
            else:
                print("Error: Timezone data not found.")
        else:
            print("Error: Coordinates not found.")
    else:
        print("Error: Address not provided.")

    return jsonify({"Error": "Could not fetch weather data"}), 400
