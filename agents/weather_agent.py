"""
Weather Agent - Handles all interactions with the OpenWeatherMap API
"""

import requests
from datetime import datetime
from typing import Dict, Any, Union

# Weather API configuration
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"


class WeatherAgent:
    """Agent responsible for handling weather data requests."""
    
    def __init__(self, api_key: str|None):
        self.api_key = api_key
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city."""
        if not city:
            return {"error": "City name is required"}
            
        url = f"{WEATHER_BASE_URL}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Weather API request timed out"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Please check your internet connection."}
        except requests.exceptions.HTTPError as e:
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    return {"error": f"City '{city}' not found. Please check the spelling."}
                elif e.response.status_code == 401:
                    return {"error": "Invalid API key for weather service"}
                else:
                    return {"error": f"Weather API error: {e.response.status_code} - {e.response.reason}"}
            else:
                return {"error": f"Weather API HTTP error: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API error: {str(e)}"}
    
    def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a city."""
        if not city:
            return {"error": "City name is required"}
            
        # Limit days to reasonable range
        days = max(1, min(days, 5))
        
        url = f"{WEATHER_BASE_URL}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Weather API request timed out"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Please check your internet connection."}
        except requests.exceptions.HTTPError as e:
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    return {"error": f"City '{city}' not found. Please check the spelling."}
                elif e.response.status_code == 401:
                    return {"error": "Invalid API key for weather service"}
                else:
                    return {"error": f"Weather API error: {e.response.status_code} - {e.response.reason}"}
            else:
                return {"error": f"Weather API HTTP error: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API error: {str(e)}"}