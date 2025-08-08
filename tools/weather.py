"""Weather tool for the LangChain Agent."""

from langchain_core.tools import tool
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# OpenWeather API configuration
OPENWEATHER_API_KEY = "bd5e378503939ddaee76f12ad7a97608"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@tool
def get_weather(location: str, unit: Optional[str] = "celsius") -> str:
    """Get the current weather for a given location.
    
    Uses the OpenWeather API to fetch real-time weather data.
    
    Args:
        location: The city and state/country, e.g. "San Francisco, CA" or "London, UK"
        unit: Temperature unit - "celsius" or "fahrenheit" (default: celsius)
        
    Returns:
        A string describing the current weather conditions
    """
    try:
        logger.info(f"Getting weather for {location} in {unit}")
        
        # Determine the unit system for the API
        if unit.lower() == "fahrenheit":
            units = "imperial"
            unit_symbol = "°F"
        else:
            units = "metric"
            unit_symbol = "°C"
        
        # API request parameters
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": units
        }
        
        # Make API request
        response = requests.get(OPENWEATHER_BASE_URL, params=params)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Extract weather information
        temperature = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        condition = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = round(data["wind"]["speed"] * 3.6, 1)  # Convert m/s to km/h
        pressure = data["main"]["pressure"]
        
        # Get location details
        city_name = data["name"]
        country = data["sys"]["country"]
        
        weather_report = (
            f"🌤️ Weather in {city_name}, {country}:\n"
            f"• Condition: {condition.title()}\n"
            f"• Temperature: {temperature}{unit_symbol}\n"
            f"• Feels Like: {feels_like}{unit_symbol}\n"
            f"• Humidity: {humidity}%\n"
            f"• Wind Speed: {wind_speed} km/h\n"
            f"• Pressure: {pressure} hPa"
        )
        
        logger.info(f"Weather report generated for {location}")
        return weather_report
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            error_msg = f"Location '{location}' not found. Please check the city name and try again."
        elif e.response.status_code == 401:
            error_msg = "API key authentication failed. Please check your API key."
        else:
            error_msg = f"API request failed with status {e.response.status_code}"
        logger.error(error_msg)
        return error_msg
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error while fetching weather data: {str(e)}"
        logger.error(error_msg)
        return error_msg
        
    except KeyError as e:
        error_msg = f"Unexpected response format from weather API: missing {str(e)}"
        logger.error(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"Sorry, I couldn't get weather information for {location}. Error: {str(e)}"
        logger.error(error_msg)
        return error_msg

# Additional weather-related tools can be added here in the future
# For example: get_forecast, get_weather_alerts, etc.