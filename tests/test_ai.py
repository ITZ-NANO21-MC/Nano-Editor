"""
Unit tests for the AI module (Phase 3 Migration).
Validates that the AI module structure, imports, and basic functionality work correctly.
"""
import sys
import os
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAIModuleImports(unittest.TestCase):
    """Test that all AI module imports resolve correctly after migration."""

    def test_import_ai_client(self):
        """ai.client.AIClient should be importable."""
        from ai.client import AIClient
        self.assertTrue(callable(AIClient))

    def test_import_ai_assistant(self):
        """ai.assistant.AIAssistant should be importable."""
        from ai.assistant import AIAssistant
        self.assertTrue(callable(AIAssistant))

    def test_import_ai_agent(self):
        """ai.agent.AIAgent should be importable."""
        from ai.agent import AIAgent
        self.assertTrue(callable(AIAgent))

    def test_import_ai_tools(self):
        """ai.tools.ToolRegistry should be importable."""
        from ai.tools import ToolRegistry
        self.assertTrue(callable(ToolRegistry))

    def test_import_ai_security(self):
        """ai.security should be importable with enums and manager."""
        from ai.security import AISecurityManager, PermissionLevel
        self.assertIsNotNone(AISecurityManager)
        self.assertIsNotNone(PermissionLevel)

    def test_import_ai_utils(self):
        """ai.utils should be importable."""
        from ai.utils import process_ai_code_output, clean_ai_json_response
        self.assertTrue(callable(process_ai_code_output))
        self.assertTrue(callable(clean_ai_json_response))

    def test_import_ai_prompts(self):
        """ai.prompts should be importable."""
        import ai.prompts as ai_prompts
        self.assertTrue(hasattr(ai_prompts, 'get_agent_system_prompt'))

    def test_import_ai_handler(self):
        """ai.handler.AIHandler should be importable."""
        from ai.handler import AIHandler
        self.assertTrue(callable(AIHandler))

    def test_import_ai_completion(self):
        """ai.completion should be importable."""
        from ai.completion import completion_engine, CompletionSuggestion
        self.assertIsNotNone(completion_engine)
        self.assertIsNotNone(CompletionSuggestion)

    def test_import_ai_file_operations(self):
        """ai.file_operations.AIFileOperations should be importable."""
        from ai.file_operations import AIFileOperations
        self.assertTrue(callable(AIFileOperations))

    def test_import_ai_ghost_text(self):
        """ai.ghost_text.GhostTextManager should be importable."""
        from ai.ghost_text import GhostTextManager
        self.assertTrue(callable(GhostTextManager))


class TestToolRegistryBasic(unittest.TestCase):
    """Test ToolRegistry basic functionality."""

    def test_instantiation(self):
        """ToolRegistry should instantiate with default tools."""
        from ai.tools import ToolRegistry
        tr = ToolRegistry()
        self.assertIsNotNone(tr)
        # ToolRegistry auto-registers 4 tools: fs_read_file, fs_list_dir, fs_write_file, terminal_run
        self.assertEqual(len(tr.get_tool_schemas()), 4)

    def test_register_and_list_no_duplicates(self):
        """ToolRegistry should register tools without duplicates."""
        from ai.tools import ToolRegistry
        tr = ToolRegistry()
        initial_count = len(tr.get_tool_schemas())
        tr.register_tool("test_tool", lambda: None, "A test tool", {"type": "object", "properties": {}})
        schemas = tr.get_tool_schemas()
        self.assertEqual(len(schemas), initial_count + 1)
        # Re-register should replace, not duplicate
        tr.register_tool("test_tool", lambda: None, "Updated desc", {"type": "object", "properties": {}})
        schemas = tr.get_tool_schemas()
        self.assertEqual(len(schemas), initial_count + 1)
        # Find our test_tool and verify description updated
        test_schema = [s for s in schemas if s["function"]["name"] == "test_tool"][0]
        self.assertEqual(test_schema["function"]["description"], "Updated desc")


class TestAISecurityBasic(unittest.TestCase):
    """Test AISecurityManager permission levels."""

    def test_safe_mode_blocks_unsafe(self):
        """SAFE mode should require approval for unsafe tools."""
        from ai.security import AISecurityManager, PermissionLevel
        mgr = AISecurityManager(PermissionLevel.SAFE)
        self.assertTrue(mgr.requires_approval("fs_write_file", {}))
        self.assertTrue(mgr.requires_approval("terminal_run", {}))

    def test_safe_mode_allows_safe(self):
        """SAFE mode should not require approval for safe tools."""
        from ai.security import AISecurityManager, PermissionLevel
        mgr = AISecurityManager(PermissionLevel.SAFE)
        self.assertFalse(mgr.requires_approval("fs_read_file", {}))
        self.assertFalse(mgr.requires_approval("fs_list_dir", {}))

    def test_autonomous_allows_all(self):
        """AUTONOMOUS mode should never require approval."""
        from ai.security import AISecurityManager, PermissionLevel
        mgr = AISecurityManager(PermissionLevel.AUTONOMOUS)
        self.assertFalse(mgr.requires_approval("fs_write_file", {}))
        self.assertFalse(mgr.requires_approval("terminal_run", {}))

    def test_paranoid_blocks_all(self):
        """PARANOID mode should require approval for everything."""
        from ai.security import AISecurityManager, PermissionLevel
        mgr = AISecurityManager(PermissionLevel.PARANOID)
        self.assertTrue(mgr.requires_approval("fs_read_file", {}))
        self.assertTrue(mgr.requires_approval("fs_list_dir", {}))


class TestAIPromptsBasic(unittest.TestCase):
    """Test AI prompts generate non-empty content."""

    def test_system_prompt_not_empty(self):
        """Agent system prompt should be non-empty."""
        import ai.prompts as ai_prompts
        prompt = ai_prompts.get_agent_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 10)


class TestCrossImports(unittest.TestCase):
    """Test that cross-imports within ai/ work correctly."""

    def test_agent_imports_client_and_tools(self):
        """AIAgent should be able to use AIClient and ToolRegistry."""
        from ai.agent import AIAgent
        from ai.client import AIClient
        from ai.tools import ToolRegistry
        # Just verifying these resolve without circular import errors
        self.assertIsNotNone(AIAgent)
        self.assertIsNotNone(AIClient)
        self.assertIsNotNone(ToolRegistry)

    def test_completion_imports_assistant(self):
        """completion module should successfully import from assistant."""
        from ai.completion import completion_engine
        self.assertIsNotNone(completion_engine)

    def test_ghost_text_imports_completion(self):
        """ghost_text should successfully import from completion."""
        from ai.ghost_text import GhostTextManager
        self.assertIsNotNone(GhostTextManager)


if __name__ == '__main__':
    unittest.main()
