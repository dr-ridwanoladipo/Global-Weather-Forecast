import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")


def get_data(place, forecast_days=None):
    """
    Fetch weather forecast data for a specific location and number of days.

    Args:
        place (str): The location for which to get the weather forecast.
        forecast_days (int, optional): The number of days to forecast. Defaults to None.

    Returns:
        list: A list of dictionaries containing the weather forecast data.
    """
    # Build the API request URL
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={place}&appid={API_KEY}"

    # Make the API request
    response = requests.get(url)
    data = response.json()

    # Filter and return data
    filtered_data = data["list"]
    nr_values = 8 * forecast_days  # Number of values to return
    filtered_data = filtered_data[:nr_values]

    return filtered_data


if __name__ == "__main__":
    # Test function with example data
    print(get_data(place="Tokyo", forecast_days=3))
