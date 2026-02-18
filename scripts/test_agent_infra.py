
import os
import sys
import logging
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_client import AIClient
from ai_tools import ToolRegistry
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_infrastructure():
    logger.info("🧪 Testing Agentic Infrastructure...")
    
    # 1. Initialize Components
    client = AIClient()
    registry = ToolRegistry()
    
    # 2. Get Tools
    tools = registry.get_tool_schemas()
    logger.info(f"🛠️  Registered Tools: {[t['function']['name'] for t in tools]}")
    
    # 3. Simulate Request
    prompt = "List the files in the current directory."
    model = config.get('AI_MODEL', 'gemini/gemini-pro')
    
    logger.info(f"🤖 Sending prompt: '{prompt}' to model: {model}")
    
    # 4. Call AI with Tools
    # Note: We need a callback that handles (content, tool_calls)
    def handle_response(content, tool_calls):
        logger.info(f"📥 Received Response:")
        logger.info(f"   Content: {content}")
        logger.info(f"   Tool Calls: {tool_calls}")
        
        if tool_calls:
            for tc in tool_calls:
                func_name = tc.function.name
                args = eval(tc.function.arguments) # Caution: eval is unsafe in prod, use json.loads
                logger.info(f"🚀 Executing Tool: {func_name} with {args}")
                
                result = registry.execute_tool(func_name, args)
                logger.info(f"✅ Result: {result}")
        else:
            logger.warning("❌ No tool calls received (Model might have just replied with text).")

    try:
        client.generate_content(
            prompt=prompt,
            model=model,
            tools=tools,
            callback=handle_response
        )
    except Exception as e:
        logger.error(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_infrastructure()
