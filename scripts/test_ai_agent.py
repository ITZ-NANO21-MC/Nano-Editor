
import os
import sys
import logging
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent import AIAgent
from ai_tools import ToolRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_agent_loop():
    logger.info("🤖 Testing AI Agent Loop...")
    
    agent = AIAgent()
    
    # Callback to print what's happening
    def on_update(event_type, message):
        icons = {
            "thinking": "🤔",
            "thought": "💭",
            "tool": "🛠️",
            "answer": "✅",
            "error": "❌"
        }
        icon = icons.get(event_type, "ℹ️")
        print(f"\n{icon} [{event_type.upper()}]: {message}")

    # Task: "List the files in the scripts folder and read test_litellm_tools.py"
    # This requires 2 steps: list_dir -> read_file
    goal = "Check what files are in the 'scripts' directory, then read the content of 'scripts/test_litellm_tools.py'."
    
    logger.info(f"🎯 Goal: {goal}")
    
    try:
        final_answer = agent.start_task(goal, callback=on_update)
        logger.info(f"\n🏁 Final Answer: {final_answer}")
    except Exception as e:
        logger.error(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_agent_loop()
