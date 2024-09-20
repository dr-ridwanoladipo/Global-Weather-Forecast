import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
from collections import Counter

# Load environment variables from a .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")


def get_data(place, forecast_days=None):
    """
    Fetch weather forecast data for a specific location and number of days.

    Args:
        place (str): The location for which to get the weather forecast
        forecast_days (int, optional): The number of days to forecast. Defaults to None.

    Returns:
        dict: A dictionary containing the weather forecast data and additional information.
    """
    # Build the API request URLs
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={place}&appid={API_KEY}&units=metric"
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={place}&appid={API_KEY}&units=metric"

    # Make the API requests
    forecast_response = requests.get(forecast_url)
    current_response = requests.get(current_url)

    if forecast_response.status_code != 200 or current_response.status_code != 200:
        raise Exception("Error fetching weather data")

    forecast_data = forecast_response.json()
    current_data = current_response.json()

    # Process and filter forecast data
    filtered_data = forecast_data["list"]

    # Calculate the end date based on the number of forecast days
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=forecast_days)

    # Filter the data to include only the specified number of days
    filtered_data = [item for item in filtered_data if
                     datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S').date() < end_date]

    # Extract additional information
    city_info = forecast_data["city"]
    timezone = pytz.FixedOffset(city_info["timezone"] // 60)
    current_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

    # Process current weather data
    current_weather = {
        "temperature": current_data["main"]["temp"],
        "feels_like": current_data["main"]["feels_like"],
        "humidity": current_data["main"]["humidity"],
        "wind_speed": current_data["wind"]["speed"],
        "description": current_data["weather"][0]["description"],
        "icon": current_data["weather"][0]["icon"],
    }

    # Calculate daily aggregates
    daily_data = {}
    for item in filtered_data:
        date = item["dt_txt"].split()[0]
        if date not in daily_data:
            daily_data[date] = {
                "temp_min": float('inf'),
                "temp_max": float('-inf'),
                "humidity": [],
                "wind_speed": [],
                "description": [],
                "icon": []
            }

        daily_data[date]["temp_min"] = min(daily_data[date]["temp_min"], item["main"]["temp_min"])
        daily_data[date]["temp_max"] = max(daily_data[date]["temp_max"], item["main"]["temp_max"])
        daily_data[date]["humidity"].append(item["main"]["humidity"])
        daily_data[date]["wind_speed"].append(item["wind"]["speed"])
        daily_data[date]["description"].append(item["weather"][0]["description"])
        daily_data[date]["icon"].append(item["weather"][0]["icon"])

    # Calculate averages and select most common values
    for date, data in daily_data.items():
        data["humidity"] = sum(data["humidity"]) / len(data["humidity"])
        data["wind_speed"] = sum(data["wind_speed"]) / len(data["wind_speed"])
        data["description"] = Counter(data["description"]).most_common(1)[0][0]
        data["icon"] = Counter(data["icon"]).most_common(1)[0][0]

    return {
        "current_weather": current_weather,
        "forecast": filtered_data,
        "daily_forecast": daily_data,
        "city_info": city_info,
        "current_time": current_time
    }


def get_air_quality(lat, lon):
    """
    Fetch air quality data for a specific location.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        dict: A dictionary containing air quality data.
    """
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error fetching air quality data")

    data = response.json()
    return data["list"][0]["main"]["aqi"]


if __name__ == "__main__":
    # Test function with example data
    print(get_data(place="Tokyo", forecast_days=3))

