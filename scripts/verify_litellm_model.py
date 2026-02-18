
import litellm
import os

from litellm import completion

# Set environment keys for litellm
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

print("Listing available LiteLLM models...")

try:
    print("Testing gemini/gemini-1.5-flash...")
    # Using mock_response string to check valid model string format
    response = completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"role": "user", "content": "Hi"}],
        mock_response="Hello!"
    )
    print("gemini/gemini-1.5-flash is VALID format")
except Exception as e:
    print(f"gemini/gemini-1.5-flash INVALID: {e}")

try:
    print("Testing gemini/gemini-2.0-flash-exp...")
    response = completion(
        model="gemini/gemini-2.0-flash-exp",
        messages=[{"role": "user", "content": "Hi"}],
        mock_response="Hello!"
    )
    print("gemini/gemini-2.0-flash-exp is VALID format")
except Exception as e:
    print(f"gemini/gemini-2.0-flash-exp INVALID: {e}")
