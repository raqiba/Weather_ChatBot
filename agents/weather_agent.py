"""
Weather Agent - Handles all interactions with the Tomorrow.io Weather API
"""

import requests
from datetime import datetime
from typing import Dict, Any, Union
import os
from dotenv import load_dotenv
load_dotenv()


# Weather API configuration
TOMORROW_API_BASE_URL = "https://api.tomorrow.io/v4/weather"


class WeatherAgent:
    """Agent responsible for handling weather data requests using Tomorrow.io API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location using Tomorrow.io API."""
        if not location:
            return {"error": "Location is required"}
            
        url = f"{TOMORROW_API_BASE_URL}/realtime"
        params = {
            "location": location,
            "apikey": self.api_key
        }
        
        # Debug: Print request details
        print(f"Making request to: {url}")
        print(f"Params: {params}")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"Response status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Response content: {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Weather API request timed out"}
        except requests.exceptions.ConnectionError as e:
            return {"error": f"Connection error. Please check your internet connection. Details: {str(e)}"}
        except requests.exceptions.HTTPError as e:
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    return {"error": f"Location '{location}' not found. Please check the spelling."}
                elif e.response.status_code == 401:
                    # Let's provide more detailed error information
                    error_detail = "Invalid or missing API key for Tomorrow.io weather service"
                    try:
                        # Try to get more details from the response
                        error_response = e.response.json()
                        if 'message' in error_response:
                            error_detail = error_response['message']
                    except:
                        pass
                    return {"error": error_detail}
                elif e.response.status_code == 400:
                    return {"error": "Bad request. Please check the location format."}
                else:
                    return {"error": f"Weather API error: {e.response.status_code} - {e.response.reason}"}
            else:
                return {"error": f"Weather API HTTP error: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API error: {str(e)}"}
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a location using Tomorrow.io API."""
        if not location:
            return {"error": "Location is required"}
            
        # Limit days to reasonable range
        days = max(1, min(days, 10))  # Tomorrow.io supports up to 10 days
        
        url = f"{TOMORROW_API_BASE_URL}/forecast"
        params = {
            "location": location,
            "apikey": self.api_key
        }
        
        # Debug: Print request details
        print(f"Making forecast request to: {url}")
        print(f"Params: {params}")
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"Forecast response status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Forecast response content: {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Weather API request timed out"}
        except requests.exceptions.ConnectionError as e:
            return {"error": f"Connection error. Please check your internet connection. Details: {str(e)}"}
        except requests.exceptions.HTTPError as e:
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    return {"error": f"Location '{location}' not found. Please check the spelling."}
                elif e.response.status_code == 401:
                    # Let's provide more detailed error information
                    error_detail = "Invalid or missing API key for Tomorrow.io weather service"
                    try:
                        # Try to get more details from the response
                        error_response = e.response.json()
                        if 'message' in error_response:
                            error_detail = error_response['message']
                    except:
                        pass
                    return {"error": error_detail}
                elif e.response.status_code == 400:
                    return {"error": "Bad request. Please check the location format."}
                else:
                    return {"error": f"Weather API error: {e.response.status_code} - {e.response.reason}"}
            else:
                return {"error": f"Weather API HTTP error: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API error: {str(e)}"}