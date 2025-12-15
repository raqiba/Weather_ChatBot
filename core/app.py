"""
Weather Agent Chatbot - Main Application Module

This module implements an agentic weather chatbot using Streamlit, 
Google Gemini AI, and Tomorrow.io Weather API.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from agents.chat_agent import ChatAgent

# Load environment variables
load_dotenv()

# Configure APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")
print("GEMINI_API_KEY loaded:", bool(GEMINI_API_KEY))
print("TOMORROW_API_KEY loaded:", bool(TOMORROW_API_KEY))
if TOMORROW_API_KEY:
    print("TOMORROW_API_KEY length:", len(TOMORROW_API_KEY))

def initialize_app():
    """Initialize the application and check dependencies."""
    # Check if API keys are available
    if not GEMINI_API_KEY or not TOMORROW_API_KEY:
        st.error("Please set both GEMINI_API_KEY and TOMORROW_API_KEY in your .env file")
        st.info("You can get your API keys from:")
        st.markdown("- [Google AI Studio](https://ai.google.dev/) for Gemini API")
        st.markdown("- [Tomorrow.io](https://www.tomorrow.io/) for Weather API")
        st.stop()

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        return client
    except Exception as e:
        st.error(f"Error initializing Gemini client: {str(e)}")
        st.stop()


def main():
    """Main application function."""
    # Initialize the app
    client = initialize_app()
    
    # Initialize the chat agent
    chat_agent = ChatAgent(client)

    # Streamlit UI
    st.set_page_config(page_title="Weather Agent Chatbot", page_icon="🌤️", layout="wide")
    
    # Custom CSS for better UI with dark theme
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stTextInput > label {
            color: #fafafa;
        }
        .stTextInput > div > input {
            background-color: #262730;
            color: #fafafa;
            border: 1px solid #4a4a4a;
        }
        .stButton > button {
            background-color: #1f77b4;
            color: white;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .user-message {
            background-color: #262730;
            border-left: 5px solid #1f77b4;
            color: #fafafa;
        }
        .assistant-message {
            background-color: #262730;
            border-left: 5px solid #2ca02c;
            color: #fafafa;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #fafafa;
        }
        .sidebar .sidebar-content {
            background-color: #0e1117;
            color: #fafafa;
        }
        .sidebar .sidebar-content a {
            color: #1f77b4;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🌤️ Weather Agent Chatbot")
    st.markdown("Ask me anything about weather! I can provide current weather, forecasts, and general weather information.")
    
    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This is an agentic weather chatbot that uses:
        - **Google Gemini AI** for natural language understanding
        - **Tomorrow.io Weather API** for real weather data
        
        ### Features:
        - Current weather information
        - Weather forecasts
        - General weather knowledge
        """)
        
        st.header("Example Questions")
        st.markdown("""
        - "What's the weather like in London?"
        - "Give me a 5-day forecast for New York"
        - "How does rain form?"
        - "Will it rain tomorrow in Tokyo?"
        """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask about weather..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show typing indicator
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Get bot response
            response = chat_agent.get_response(prompt, st.session_state.messages)
            
            # Render response - now it's always text/markdown from the LLM
            if isinstance(response, dict):
                # This shouldn't happen anymore, but just in case
                message_placeholder.markdown(str(response))
            else:
                # Display the LLM-generated markdown/text response
                message_placeholder.markdown(response)
        
        # Add bot response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": str(response)
        })


if __name__ == "__main__":
    main()