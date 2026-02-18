
import os
import json
import logging
from typing import List, Dict, Any
import litellm
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock tool definition
def get_current_weather(location: str, unit: str = "celsius"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

# Tool schema for LiteLLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

def test_tool_calling():
    # Only test if API key is set
    model = config.get('AI_MODEL', 'gemini/gemini-2.0-flash')
    api_key = config.get('GEMINI_API_KEY')
    
    if not api_key:
        logger.error("No API Key found in config. Please set GEMINI_API_KEY.")
        return

    logger.info(f"Testing tool calling with model: {model}")
    
    messages = [{"role": "user", "content": "What's the weather like in San Francisco?"}]
    
    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            api_key=api_key
        )
        
        message = response.choices[0].message
        logger.info(f"Model Response: {message}")
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            logger.info("✅ Tool call detected!")
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                logger.info(f"Function: {function_name}")
                logger.info(f"Arguments: {arguments}")
                
                if function_name == "get_current_weather":
                    result = get_current_weather(**arguments)
                    logger.info(f"Execution Result: {result}")
        else:
            logger.warning("❌ No tool call generated.")
            
    except Exception as e:
        logger.error(f"Error calling LiteLLM: {e}")

if __name__ == "__main__":
    test_tool_calling()
