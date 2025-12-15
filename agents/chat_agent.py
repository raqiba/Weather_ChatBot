"""
Chat Agent - Main coordinator that processes user queries and determines appropriate actions
"""

import json
import os
from typing import Dict, Any, List
from google import genai
from agents.weather_agent import WeatherAgent
from dotenv import load_dotenv

load_dotenv()
# Configure APIs
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")
print("Weather API key loaded in chat_agent:", bool(TOMORROW_API_KEY))
if TOMORROW_API_KEY:
    print("Weather API key length:", len(TOMORROW_API_KEY))
else:
    print("Available environment variables:", list(os.environ.keys()))


class ChatAgent:
    """Main agent that coordinates user queries and responses."""
    
    def __init__(self, client: genai.Client):
        self.model = client
        self.weather_agent = WeatherAgent(TOMORROW_API_KEY)
    
    def process_query(self, user_query: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process user query and determine appropriate action."""
        # Use Gemini to understand the query and decide what to do
        prompt = f"""
        You are a weather assistant. Based on the user's query, determine what action to take.
        Possible actions are:
        1. "current_weather" - for current weather information
        2. "forecast" - for weather forecast
        3. "general" - for general weather questions
        
        Also extract any relevant parameters like city name from the query.
        
        User query: "{user_query}"
        
        Respond ONLY in JSON format with action and parameters:
        {{
            "action": "action_type",
            "parameters": {{
                "city": "city_name_if_applicable",
                "days": number_of_days_if_applicable
            }}
        }}
        
        IMPORTANT: Respond ONLY with the JSON, no other text.
        """
        
        try:
            response = self.model.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            # Access the text content properly
            if hasattr(response, 'text'):
                clean_response = response.text
            else:
                # Handle different response format
                clean_response = str(response)
            # Clean up the response text
            clean_response = response.text.strip()
            # Remove any markdown code block indicators
            if clean_response.startswith("```"):
                clean_response = clean_response[3:].strip()
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:].strip()
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3].strip()
            
            # Find the first { and last } to extract JSON
            start_idx = clean_response.find('{')
            end_idx = clean_response.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                clean_response = clean_response[start_idx:end_idx+1]
            
            # Parse the JSON response
            action_data = json.loads(clean_response)
            return action_data
        except json.JSONDecodeError as e:
            # If JSON parsing fails, fallback to general response
            print("Could not parse action from AI response. Using general action.")
            return {
                "action": "general",
                "parameters": {}
            }
        except Exception as e:
            # Handle other exceptions
            print("Error processing query. Using general action.")
            return {
                "action": "general",
                "parameters": {}
            }
    
    def get_response(self, user_query: str, chat_history: List[Dict[str, str]]) -> Any:
        """Get appropriate response based on query analysis."""
        # Process the query to determine action
        action_data = self.process_query(user_query, chat_history)
        action = action_data.get("action", "general")
        parameters = action_data.get("parameters", {})
        
        if action == "current_weather":
            location = parameters.get("location") or parameters.get("city")
            if location:
                print(f"Fetching current weather for: {location}")
                weather_data = self.weather_agent.get_current_weather(location)
                print(f"Weather data received: {type(weather_data)}")
                if "error" in weather_data:
                    print(f"Weather API error: {weather_data['error']}")
                    return f"Sorry, I couldn't get the weather information for {location}. Error: {weather_data['error']}"
                
                # Send raw weather data to LLM for natural language composition
                context = "\n".join([f"User: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}" 
                                    for msg in chat_history[-3:]])  # Last 3 messages for context
                
                prompt = f"""
                You are a helpful weather assistant. The user asked about the current weather in {location}.
                Here is the raw weather data from the Tomorrow.io API:
                
                {json.dumps(weather_data, indent=2)}
                
                Please provide a friendly, natural language response that includes the most important information.
                Focus on these key aspects:
                1. Current temperature and how it feels
                2. Weather conditions (sunny, cloudy, rainy, etc.)
                3. Humidity and wind information
                4. Any notable weather phenomena
                
                Format your response in a clear, readable way. You can use formatting if appropriate.
                Keep your response concise but informative. Use emojis where appropriate to make it visually appealing.
                Do not include the raw JSON data in your response - translate it into natural language.
                
                Recent conversation context:
                {context}
                
                User's question: {user_query}
                """
                
                try:
                    print("Sending request to Gemini AI...")
                    response = self.model.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    print("Received response from Gemini AI")
                    # Access the text content properly
                    if hasattr(response, 'text'):
                        return response.text
                    else:
                        # Handle different response format
                        return str(response)
                except Exception as e:
                    print(f"Gemini AI error: {str(e)}")
                    # Fallback to extracting key information if LLM fails
                    try:
                        # Extract key information from Tomorrow.io response
                        data = weather_data.get('data', {})
                        values = data.get('values', {}) if isinstance(data, dict) else {}
                        location_info = weather_data.get('location', {}) if isinstance(weather_data, dict) else {}
                        
                        # Extract values
                        temp = values.get('temperature')
                        apparent_temp = values.get('temperatureApparent')
                        humidity = values.get('humidity')
                        wind_speed = values.get('windSpeed')
                        wind_direction = values.get('windDirection')
                        weather_code = values.get('weatherCode')
                        visibility = values.get('visibility')
                        
                        # Get location name
                        loc_name = location_info.get('name', location) if isinstance(location_info, dict) else location
                        
                        # Create a simple text response
                        response_text = f"🌤️ Current weather in {loc_name}:\n\n"
                        if temp is not None:
                            response_text += f"🌡️ Temperature: {temp}°C"
                            if apparent_temp is not None:
                                response_text += f" (Feels like {apparent_temp}°C)\n"
                            else:
                                response_text += "\n"
                        if humidity is not None:
                            response_text += f"💧 Humidity: {humidity}%\n"
                        if wind_speed is not None:
                            direction = f" from {wind_direction}°" if wind_direction is not None else ""
                            response_text += f"💨 Wind: {wind_speed} m/s{direction}\n"
                        if visibility is not None:
                            response_text += f"👁️ Visibility: {visibility} km\n"
                        
                        return response_text or "Unable to extract weather information."
                    except (KeyError, IndexError, TypeError) as e:
                        return f"Sorry, I couldn't parse the weather data. Error: {str(e)}"
            else:
                return "Please specify a location to get the current weather."
        
        elif action == "forecast":
            location = parameters.get("location") or parameters.get("city")
            days = parameters.get("days", 5)
            if location:
                print(f"Fetching forecast for: {location}")
                forecast_data = self.weather_agent.get_forecast(location)
                print(f"Forecast data received: {type(forecast_data)}")
                if "error" in forecast_data:
                    print(f"Forecast API error: {forecast_data['error']}")
                    return f"Sorry, I couldn't get the forecast for {location}. Error: {forecast_data['error']}"
                
                # Send raw forecast data to LLM for natural language composition
                context = "\n".join([f"User: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}" 
                                    for msg in chat_history[-3:]])  # Last 3 messages for context
                
                prompt = f"""
                You are a helpful weather assistant. The user asked for a weather forecast for {location}.
                Here is the raw forecast data from the Tomorrow.io API:
                
                {json.dumps(forecast_data, indent=2)}
                
                Please provide a friendly, natural language response that includes the most important information.
                Organize the forecast in a clear, readable format, day by day.
                For each day/time period, include:
                1. Date and time
                2. Temperature (and feels like temperature if available)
                3. Weather conditions
                4. Precipitation probability
                5. Wind information
                6. Notable weather phenomena
                
                You can use formatting, lists, or any other format that best presents the data.
                Use emojis to make the forecast visually appealing.
                Keep your response concise but informative.
                Do not include the raw JSON data in your response - translate it into natural language.
                
                Recent conversation context:
                {context}
                
                User's question: {user_query}
                """
                
                try:
                    print("Sending forecast request to Gemini AI...")
                    response = self.model.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    print("Received forecast response from Gemini AI")
                    # Access the text content properly
                    if hasattr(response, 'text'):
                        return response.text
                    else:
                        # Handle different response format
                        return str(response)
                except Exception as e:
                    print(f"Gemini AI forecast error: {str(e)}")
                    # Fallback to extracting key information if LLM fails
                    try:
                        # Extract key information from Tomorrow.io forecast response
                        timelines = forecast_data.get('timelines', {})
                        location_info = forecast_data.get('location', {}) if isinstance(forecast_data, dict) else {}
                        
                        # Get location name
                        loc_name = location_info.get('name', location) if isinstance(location_info, dict) else location
                        
                        # Process timeline data - handle different timeline types
                        if timelines and isinstance(timelines, dict):
                            # Try to get minutely data first, then hourly, then daily
                            forecast_entries = []
                            if 'minutely' in timelines and isinstance(timelines['minutely'], list):
                                forecast_entries = timelines['minutely']
                            elif 'hourly' in timelines and isinstance(timelines['hourly'], list):
                                forecast_entries = timelines['hourly']
                            elif 'daily' in timelines and isinstance(timelines['daily'], list):
                                forecast_entries = timelines['daily']
                            
                            if forecast_entries:
                                response_text = f"🌤️ Weather forecast for {loc_name}:\n\n"
                                
                                # Show first few entries
                                for i, entry in enumerate(forecast_entries[:10]):  # Show first 10 entries
                                    if isinstance(entry, dict):
                                        time = entry.get('time', 'N/A')
                                        values = entry.get('values', {}) if isinstance(entry, dict) else {}
                                        
                                        # Extract values
                                        temp = values.get('temperature')
                                        apparent_temp = values.get('temperatureApparent')
                                        humidity = values.get('humidity')
                                        wind_speed = values.get('windSpeed')
                                        weather_code = values.get('weatherCode')
                                        precipitation_prob = values.get('precipitationProbability')
                                        
                                        response_text += f"⏰ {time}:\n"
                                        if temp is not None:
                                            temp_str = f"{temp}°C"
                                            if apparent_temp is not None:
                                                temp_str += f" (Feels like {apparent_temp}°C)"
                                            response_text += f"   🌡️ {temp_str}\n"
                                        if humidity is not None:
                                            response_text += f"   💧 Humidity: {humidity}%\n"
                                        if precipitation_prob is not None:
                                            response_text += f"   🌧️ Precipitation: {precipitation_prob}%\n"
                                        if wind_speed is not None:
                                            response_text += f"   💨 Wind: {wind_speed} m/s\n"
                                        response_text += "\n"
                                
                                return response_text
                                
                        return "Unable to extract forecast information."
                    except (KeyError, IndexError, TypeError, ValueError) as e:
                        return f"Sorry, I couldn't parse the forecast data. Error: {str(e)}"
            else:
                return "Please specify a location to get the weather forecast."
        
        else:  # general action
            # Use Gemini for general weather questions
            context = "\n".join([f"User: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}" 
                                for msg in chat_history[-5:]])  # Last 5 messages for context
            
            prompt = f"""
            You are a helpful weather assistant. Answer the user's question based on your knowledge about weather.
            Keep your responses concise and informative. Use emojis where appropriate to make your responses visually appealing.
            
            Conversation history:
            {context}
            
            User's latest question: {user_query}
            """
            
            try:
                response = self.model.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                # Access the text content properly
                if hasattr(response, 'text'):
                    return response.text
                else:
                    # Handle different response format
                    return str(response)
            except Exception as e:
                return f"Sorry, I'm having trouble processing your request right now. Error: {str(e)}"