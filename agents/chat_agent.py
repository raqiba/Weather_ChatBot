"""
Chat Agent - Main coordinator that processes user queries and determines appropriate actions
"""

import json
import os
from typing import Dict, Any, List
from google import genai
from agents.weather_agent import WeatherAgent

# Configure APIs
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


class ChatAgent:
    """Main agent that coordinates user queries and responses."""
    
    def __init__(self, client: genai.Client):
        self.model = client
        self.weather_agent = WeatherAgent(WEATHER_API_KEY)
        
    
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
            city = parameters.get("city")
            if city:
                weather_data = self.weather_agent.get_current_weather(city)
                if "error" in weather_data:
                    return f"Sorry, I couldn't get the weather information for {city}. Error: {weather_data['error']}"
                
                # Return structured data for current weather
                try:
                    # Extract values with proper type checking
                    main_data = weather_data.get('main', {}) if isinstance(weather_data.get('main'), dict) else {}
                    weather_list = weather_data.get('weather', []) if isinstance(weather_data.get('weather'), list) else []
                    wind_data = weather_data.get('wind', {}) if isinstance(weather_data.get('wind'), dict) else {}
                    
                    temp = main_data.get('temp') if isinstance(main_data, dict) else None
                    description = weather_list[0].get('description') if isinstance(weather_list, list) and len(weather_list) > 0 and isinstance(weather_list[0], dict) else 'Unknown'
                    humidity = main_data.get('humidity') if isinstance(main_data, dict) else None
                    wind_speed = wind_data.get('speed') if isinstance(wind_data, dict) else None
                    updated = weather_data.get('dt') if isinstance(weather_data, dict) else None
                    
                    # Validate that we have the required data
                    if temp is None or humidity is None or wind_speed is None:
                        return "Sorry, some weather data is missing."
                        
                    # Ensure description is a string
                    if description is None:
                        description = 'Unknown'
                    elif not isinstance(description, str):
                        description = str(description)
                    
                    # Return structured data
                    return {
                        "type": "current",
                        "city": city,
                        "units": "metric",
                        "temp": temp,
                        "condition": description,
                        "humidity": humidity,
                        "wind_speed": wind_speed,
                        "updated": updated
                    }
                except (KeyError, IndexError, TypeError) as e:
                    return f"Sorry, I couldn't parse the weather data. Error: {str(e)}"
            else:
                return "Please specify a city to get the current weather."
        
        elif action == "forecast":
            city = parameters.get("city")
            days = parameters.get("days", 5)
            if city:
                forecast_data = self.weather_agent.get_forecast(city)
                if "error" in forecast_data:
                    return f"Sorry, I couldn't get the forecast for {city}. Error: {forecast_data['error']}"
                
                # Return structured data for forecast
                try:
                    forecast_list = forecast_data.get('list', [])[:days*8]  # 8 forecasts per day (every 3 hours)
                    
                    # Return structured data
                    return {
                        "type": "forecast",
                        "city": city,
                        "units": "metric",
                        "days": days,
                        "list": forecast_list
                    }
                except (KeyError, IndexError, TypeError, ValueError) as e:
                    return f"Sorry, I couldn't parse the forecast data. Error: {str(e)}"
            else:
                return "Please specify a city to get the weather forecast."
        
        else:  # general action
            # Use Gemini for general weather questions
            context = "\n".join([f"User: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}" 
                                for msg in chat_history[-5:]])  # Last 5 messages for context
            
            prompt = f"""
            You are a helpful weather assistant. Answer the user's question based on your knowledge about weather.
            Keep your responses concise and informative.
            
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