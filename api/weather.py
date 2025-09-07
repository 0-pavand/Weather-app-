import requests
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # A mapping of WMO Weather Codes to descriptions
        wmo_weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing drizzle",
            57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            66: "Light freezing rain", 67: "Heavy freezing rain", 71: "Slight snow fall",
            73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains", 80: "Slight rain showers",
            81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers",
            86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }

        # Parse the URL to get query parameters
        from urllib.parse import urlparse, parse_qs
        query_params = parse_qs(urlparse(self.path).query)
        city_name = query_params.get('city', [''])[0]

        if not city_name:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "City name is required."}
            self.wfile.write(json.dumps(response).encode())
            return

        # Step 1: Geocoding API call to get coordinates
        geocoding_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json'
        try:
            geo_response = requests.get(geocoding_url)
            geo_response.raise_for_status()
            geocoding_data = geo_response.json()

            if not geocoding_data.get('results'):
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": f"Could not find coordinates for '{city_name}'."}
                self.wfile.write(json.dumps(response).encode())
                return
            
            result = geocoding_data['results'][0]
            latitude = result['latitude']
            longitude = result['longitude']

            # Step 2: Weather forecast API call using the coordinates
            weather_url = (
                f'https://api.open-meteo.com/v1/forecast?'
                f'latitude={latitude}&longitude={longitude}&'
                f'current=temperature_2m,relative_humidity_2m,weather_code,apparent_temperature&'
                f'temperature_unit=celsius'
            )
            
            weather_response = requests.get(weather_url)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            current = weather_data['current']
            
            weather_description = wmo_weather_codes.get(current['weather_code'], "Unknown weather condition")
            
            final_data = {
                "city": city_name,
                "weather_description": weather_description,
                "temperature": current['temperature_2m'],
                "feels_like": current['apparent_temperature'],
                "humidity": current['relative_humidity_2m']
            }
            
            # Send the successful response back to the frontend
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(final_data).encode())

        except requests.exceptions.RequestException as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": f"Internal server error: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
