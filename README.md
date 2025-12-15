# Weather Agent Chatbot

An agentic-based weather chatbot built with Streamlit that integrates Google Gemini AI and OpenWeatherMap API to provide weather information and answer weather-related questions.

## Project Structure

```
Weather_Project/
├── agents/
│   ├── __init__.py
│   ├── weather_agent.py      # Handles OpenWeatherMap API interactions
│   └── chat_agent.py         # Main coordinator that processes user queries
├── core/
│   ├── __init__.py
│   └── app.py               # Main Streamlit application
├── utils/
│   ├── __init__.py
│   └── formatter.py         # Utility functions for formatting responses
├── run.py                   # Entry point for the application
├── .env                     # API keys (not included in repo)
├── requirements.txt         # Python dependencies
├── run.bat                  # Windows script to run the application
└── setup.bat                # Windows script to install dependencies
```

## Features

- Current weather information for any city
- Weather forecasts for upcoming days
- General weather knowledge using AI
- Conversational interface with chat history
- Multi-agent architecture for specialized tasks

## Prerequisites

1. Python 3.7 or higher
2. API keys for:
   - Google Gemini API ([Get it here](https://ai.google.dev/))
   - OpenWeatherMap API ([Get it here](https://openweathermap.org/api))

## Setup

### Option 1: Manual Setup

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   WEATHER_API_KEY=your_openweathermap_api_key_here
   ```

### Option 2: Windows Setup

1. Clone or download this repository
2. Double-click on `setup.bat` to install dependencies
3. Edit the `.env` file to add your API keys
4. Double-click on `run.bat` to start the application

## Usage

### Command Line

Run the Streamlit app:
```
streamlit run run.py
```

### Windows

Double-click on `run.bat` to start the application

The app will open in your default browser. You can ask questions like:
- "What's the weather like in London?"
- "Give me a 5-day forecast for New York"
- "How does rain form?"
- "Will it rain tomorrow in Tokyo?"

## Architecture

The application uses an agentic architecture with specialized agents:

### 1. WeatherAgent (`agents/weather_agent.py`)
- Handles all interactions with the OpenWeatherMap API
- Provides methods for current weather and forecast data
- Includes robust error handling for API issues

### 2. ChatAgent (`agents/chat_agent.py`)
- Main coordinator that processes user queries
- Uses Gemini AI to understand user intent
- Routes requests to appropriate handlers
- Manages conversation history

### 3. Formatter Utilities (`utils/formatter.py`)
- Contains functions for formatting weather data into readable markdown
- Provides consistent presentation for current weather and forecasts

### 4. Core Application (`core/app.py`)
- Implements the Streamlit UI
- Manages user interface components
- Handles chat history display
- Integrates all components together

## How It Works

1. User inputs a weather-related query
2. ChatAgent analyzes the query using Gemini AI to determine the intent
3. Based on the intent, the appropriate action is taken:
   - Current weather requests are handled by WeatherAgent
   - Forecast requests are handled by WeatherAgent
   - General questions are answered using Gemini AI
4. Results are formatted using the formatter utilities
5. Formatted results are presented to the user in a conversational interface

## Troubleshooting

- If you get import errors, make sure you've run `pip install -r requirements.txt`
- If you get API key errors, check that your `.env` file is correctly configured
- If you get connection errors, check your internet connection

## Customization

You can customize the application by modifying:
- `agents/chat_agent.py`: Adjust prompt templates or add new agent capabilities
- `agents/weather_agent.py`: Modify API interaction logic or add new weather data sources
- `utils/formatter.py`: Change how weather data is presented to users
- `core/app.py`: Modify UI components or add new interface elements

## License

This project is open source and available under the MIT License.