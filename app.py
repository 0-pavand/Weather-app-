import requests

city_name = input("Enter the city name : ")

geocoding_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json'

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

response = requests.get(geocoding_url)
geocoding_data = response.json()

if 'results' in geocoding_data and len(geocoding_data['results']) > 0:
    result = geocoding_data['results'][0]
    latitude = result['latitude']
    longitude = result['longitude']

    print(f"Coordinates for {city_name}: Latitude={latitude}, Longitude={longitude}")
    
else:
    print(f"Error: Could not find coordinates for '{city_name}'. Please check the spelling.")

url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,weather_code,apparent_temperature&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    current= data['current']
    weather_code = current['weather_code']
    weather_description = wmo_weather_codes.get(current['weather_code'], "Unknown weather condition")
    print("Weather is ", weather_description)
    print("Current temperature is ", current['temperature_2m'])
    print("Current temperature feels like ", current['apparent_temperature'])
    print("Humidiy is ", current['relative_humidity_2m'])
else:
    print(f"Error fetching data: {response.status_code}")