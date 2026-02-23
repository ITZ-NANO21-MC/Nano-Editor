"""
AI Agent Logic (The Brain)
Implements the ReAct loop (Reasoning + Acting) for autonomous tasks.
"""
import json
import traceback
from typing import List, Dict, Any, Optional, Callable
from config import config
from logger import logger
from ai.client import AIClient
from ai.tools import ToolRegistry
import ai.prompts as ai_prompts
from ai.security import AISecurityManager, PermissionLevel

class AIAgent:
    """Autonomous Agent capable of using tools to solve complex tasks."""

    def __init__(self):
        self.client = AIClient()
        self.tools = ToolRegistry()
        self.security = AISecurityManager(PermissionLevel.SAFE)
        self.max_steps = 10  # Prevent infinite loops
        self.history: List[Dict[str, Any]] = []
        
    def start_task(
        self, 
        user_goal: str, 
        project_context: str = "", 
        callback: Optional[Callable[[str, Optional[str]], None]] = None,
        approval_callback: Optional[Callable[[str, Dict[str, Any]], bool]] = None
    ):
        """
        Start the agent loop for a given goal.
        
        Args:
            user_goal: The user's request.
            project_context: Context about the project (file tree, etc.)
            callback: Function to call with updates (status, final_answer).
                      callback("thinking", "Analyzing...")
                      callback("tool", "Executing: ls -la")
                      callback("answer", "Here is the result...")
            approval_callback: Function called when a tool needs user approval. Returns True if approved.
        """
        self.history = []
        
        # 1. System Prompt
        system_prompt = ai_prompts.get_agent_system_prompt(project_context)
        # We don't send system prompt as a separate message if the API doesn't support it well,
        # but for now we'll prepend it to the first user message or use it if the client supports it.
        # LiteLLM/Gemini usually handles system prompts via 'system' role or prepending.
        # For simplicity with current AIClient, we'll prepend.
        
        full_prompt = f"{system_prompt}\n\nUser Goal: {user_goal}"
        
        # 2. Add to history
        self.history.append({"role": "user", "content": full_prompt})
        
        step_count = 0
        while step_count < self.max_steps:
            step_count += 1
            logger.info(f"🔄 Agent Step {step_count}/{self.max_steps}")
            
            try:
                # 3. Call Model
                if callback: callback("thinking", f"Step {step_count}: Reasoning...")
                
                # We need to construct the messages list for the client
                # Currently AIClient.generate_content takes a prompt string, but for chat/agent 
                # we really need a list of messages. 
                # modification to AIClient might be needed to support passing `messages` directly
                # or we convert history to a string (less ideal for tool use).
                #
                # WORKAROUND: For this phase, we will assume AIClient needs an update to accept `messages`
                # or we use the `litellm` call directly here for the loop. 
                #
                # Actually, AIClient.generate_content wraps litellm.completion. 
                # If we pass the whole history as a "prompt" formatted as a chat log? 
                # No, tool calling relies on the messages structure.
                #
                # Let's use AIClient but we might need to extend it to accept `messages` list 
                # instead of just `prompt` string.
                #
                # For now, let's assume we can pass the last message as prompt and keep internal history? 
                # No, stateless.
                
                # Let's bypass AIClient.generate_content for now and call litellm directly OR 
                # update AIClient to support `messages`. 
                # The latter is better for architecture.
                # But for now, let's verify if AIClient.generate_content supports list of messages?
                # No, it takes `prompt: str`.
                
                # Let's convert history to a single prompt if model implies straightforward text generation,
                # BUT tool calling requires structured messages.
                
                # REFACTOR DECISION: I will upgrade AIClient to accept `messages: List[Dict]` 
                # in a separate method `chat_completion` or overload `generate_content`.
                # For this file, I'll use a protected method from AIClient or just instantiate litellm locally 
                # to prove the concept, then refactor AIClient.
                # Wait, AIClient is a wrapper. I should use it.
                
                # Let's use a temporary method in the agent to call litellm, 
                # essentially duplicating AIClient's wrapper logic but for chat,
                # until we properly refactor AIClient for Chat/Agent support.
                
                response = self._call_llm(self.history, tools=self.tools.get_tool_schemas())
                
                if not response.choices:
                    logger.error("Empty response from LLM (no choices)")
                    if callback: callback("error", "The model returned an empty response. Retrying...")
                    continue
                
                message = response.choices[0].message
                content = message.content
                tool_calls = getattr(message, 'tool_calls', None)
                
                # 4. Handle Response
                if content:
                    logger.info(f"🤖 Agent Thought: {content}")
                    self.history.append({"role": "assistant", "content": content})
                    if callback: callback("thought", content)
                
                if tool_calls:
                    # Serialize to clean dict to avoid Pydantic issues on next call
                    tool_calls_list = []
                    for tc in tool_calls:
                        tool_calls_list.append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        })
                    assistant_msg = {"role": "assistant", "content": content or "", "tool_calls": tool_calls_list}
                    self.history.append(assistant_msg)
                    
                    for tc in tool_calls:
                        func_name = tc.function.name
                        func_args_str = tc.function.arguments
                        func_id = tc.id
                        
                        if callback: callback("tool", f"Executing {func_name}...")
                        
                        # Execute
                        try:
                            func_args = json.loads(func_args_str)
                            
                            # Security Check
                            if self.security.requires_approval(func_name, func_args):
                                if approval_callback:
                                    if callback: callback("system", f"⚠️ Asking permission to run {func_name}...")
                                    approved = approval_callback(func_name, func_args)
                                else:
                                    approved = False
                                    logger.warning(f"Approval required for {func_name} but no callback provided.")
                            else:
                                approved = True
                                
                            if approved:
                                result = self.tools.execute_tool(func_name, func_args)
                            else:
                                result = "Error: Tool execution denied by user."
                        except Exception as e:
                            result = f"Error processing tool call: {e}"
                        
                        logger.info(f"🛠️ Tool Output ({func_name}): {result}")
                        
                        # Add tool result to history
                        self.history.append({
                            "role": "tool",
                            "tool_call_id": func_id,
                            "name": func_name,
                            "content": str(result)
                        })
                else:
                    # No tool calls -> Final Answer or Question
                    logger.info("✅ Agent finished (no more tools).")
                    if callback: callback("answer", content)
                    return content

            except Exception as e:
                logger.error(f"❌ Agent Loop Error: {e}")
                logger.error(traceback.format_exc())
                if callback: callback("error", str(e))
                return f"Error: {e}"
        
        return "Max steps reached."

    def _call_llm(self, messages, tools=None):
        """Use AIClient for chat completions."""
        model = config.get('AI_MODEL', 'gemini/gemini-2.0-flash-exp')
        return self.client.chat_completion(
            messages=messages,
            model=model,
            tools=tools
        )
