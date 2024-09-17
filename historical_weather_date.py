import requests
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
from weather_stations_db import insert_station, insert_weather_data


class WeatherManager:
    def __init__(self):
        self.station_id = None
        self.api_token = 'FyGLLaCfXSCylvrvBfrhkeMQLdqcoMtv'

    def constructAPI(self, category):
        base_url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/'
        return f"{base_url}{category}"

    def get_station(self, extent):
        API_url = self.constructAPI('stations')
        headers = {'token': self.api_token}
        params = {'extent': extent}

        try:
            response = requests.get(API_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stations: {e}")
            return []

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0088
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def get_closest_station(self, lat, lon):
        closest_station = None
        min_distance = float('inf')
        target_lat, target_lon = float(lat), float(lon)
        extent = f"{target_lat - 0.5},{target_lon - 0.5},{target_lat + 0.5},{target_lon + 0.5}"

        stations = self.get_station(extent)
        for station in stations:
            station_lat = station.get('latitude')
            station_lon = station.get('longitude')
            if station_lat and station_lon:
                distance = self.haversine(target_lat, target_lon, station_lat, station_lon)
                if distance < min_distance:
                    min_distance = distance
                    closest_station = station

        self.station_id = closest_station.get('id') if closest_station else None

        return closest_station

    def get_data(self, datasetid, start_date, end_date, stationid, datatypeid):
        api_url = self.constructAPI('data?')
        headers = {'token': self.api_token}
        params = {
            'datasetid': datasetid,
            'startdate': start_date,
            'enddate': end_date,
            'stationid': stationid,
            'datatypeid': datatypeid,
            'limit': 1000
        }
        try:
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical weather data: {e}")
            return []

    def insert_closest_station(self, closest_station):
        if not self.station_id:
            print("Station ID is empty")
            return

        if not isinstance(closest_station, dict):
            print(f"Invalid closest station data: {closest_station}")
            return

        station_data = {
            'id': closest_station.get('id'),
            'station_name': closest_station.get('name'),
            'latitude': closest_station.get('latitude'),
            'longitude': closest_station.get('longitude'),
            'elevation': closest_station.get('elevation'),
            'mindate': closest_station.get('mindate'),
            'maxdate': closest_station.get('maxdate'),
            'datacoverage': closest_station.get('datacoverage'),
        }
        insert_station(station_data)

def function_call(lat, lon):
    weather_manager = WeatherManager()
    closest_station = weather_manager.get_closest_station(lat, lon)
    weather_manager.insert_closest_station(closest_station)
