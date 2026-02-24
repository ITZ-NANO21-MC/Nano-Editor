import customtkinter
import threading
import json
from typing import Callable, Optional
from ai.agent import AIAgent
from ai.utils import process_ai_code_output
from core.syntax_highlighter import SyntaxHighlighter

class AgentPanel(customtkinter.CTkFrame):
    """
    Panel for the Autonomous Agent (Nano-Agent).
    Visualizes the ReAct loop: Goal -> Thoughts -> Actions -> Results.
    """
    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.agent = AIAgent()
        self.is_running = False
        self.thread = None

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1) # Content
        self.grid_rowconfigure(1, weight=0) # Input
        self.grid_columnconfigure(0, weight=1)

        # 1. Trace Area (Scrollable)
        self.trace_view = customtkinter.CTkScrollableFrame(
            self,
            fg_color=("#FFFFFF", "#1E1E1E"),
            scrollbar_button_color=("#CCCCCC", "#3E3E3E"),
            scrollbar_button_hover_color=("#BBBBBB", "#4E4E4E")
        )
        self.trace_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 2. Input Area
        self.input_frame = customtkinter.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.goal_entry = customtkinter.CTkEntry(
            self.input_frame,
            placeholder_text="Describe a complex task (e.g., 'Find and fix the bug in utils.py')...",
            height=40,
            font=("Segoe UI", 12)
        )
        self.goal_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.goal_entry.bind("<Return>", lambda e: self.start_agent())

        self.action_btn = customtkinter.CTkButton(
            self.input_frame,
            text="🚀 Start Agent",
            command=self.start_agent,
            width=100,
            height=40,
            font=("Segoe UI", 12, "bold"),
            fg_color="#107C10", # Green
            hover_color="#0E6B0E"
        )
        self.action_btn.grid(row=0, column=1, sticky="e")

        # Welcome Message
        self._add_trace_item("system", "🤖 Nano-Agent Ready.\nDescribe a task and I will perform actions to solve it.")
        
        # Override terminal_run to use the real TerminalPanel
        if self.app:
            def terminal_run_blocking(command):
                if hasattr(self.app, 'terminal'):
                    # self.app.terminal is the TerminalPanel instance (aliased in editor_view_v3)
                    return self.app.terminal.run_command_blocking(command)
                return "Error: Terminal not available."

            self.agent.tools.register_tool(
                "terminal_run",
                terminal_run_blocking,
                "Run a terminal command securely via the integrated terminal and return the output.",
                {"type": "object", "properties": {"command": {"type": "string"}}}
            )

    def start_agent(self):
        """Start the agent loop in a thread."""
        if self.is_running: return
        
        goal = self.goal_entry.get().strip()
        if not goal: return

        self.is_running = True
        self.action_btn.configure(state="disabled", text="Running...", fg_color="#333333")
        self.goal_entry.configure(state="disabled")
        
        # Clear previous if desired, or keep history. Let's keep for now but add separator
        self._add_trace_item("separator", "--- New Task ---")
        self._add_trace_item("user", f"🎯 Goal: {goal}")

        # Get context
        project_context = ""
        if self.app and hasattr(self.app, '_get_project_context'):
             project_context = self.app._get_project_context()

        # Run in thread
        self.thread = threading.Thread(
            target=self._run_agent_thread,
            args=(goal, project_context),
            daemon=True
        )
        self.thread.start()

    def _run_agent_thread(self, goal, context):
        """Worker thread for agent."""
        try:
            self.agent.start_task(
                user_goal=goal,
                project_context=context,
                callback=self._agent_callback,
                approval_callback=self._agent_approval_callback
            )
        except Exception as e:
            self._agent_callback("error", str(e))
        finally:
            self.after(0, self._reset_ui)

    def _agent_callback(self, event_type, message):
        """Callback from agent to update UI."""
        self.after(0, lambda: self._add_trace_item(event_type, message))

    def _agent_approval_callback(self, tool_name, tool_args) -> bool:
        """Called from agent thread. Shows dialog on main thread, blocks until choice."""
        result_container = []
        event = threading.Event()
        
        def show_dialog():
            dialog = customtkinter.CTkToplevel(self)
            dialog.title("Security: Approval Required")
            dialog.geometry("450x300")
            dialog.attributes("-topmost", True)
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set() # Make modal
            
            # Content
            content_frame = customtkinter.CTkScrollableFrame(dialog, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))
            
            title_lbl = customtkinter.CTkLabel(content_frame, text=f"⚠️ Agent request to execute:\n{tool_name}", font=("Segoe UI", 14, "bold"))
            title_lbl.pack(anchor="w", pady=(0, 10))
            
            args_str = json.dumps(tool_args, indent=2)
            args_lbl = customtkinter.CTkLabel(content_frame, text=args_str, font=("Consolas", 11), justify="left")
            args_lbl.pack(anchor="w")
            
            # Buttons
            btn_frame = customtkinter.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(side="bottom", fill="x", padx=20, pady=20)
            
            def handle_result(approved):
                result_container.append(approved)
                dialog.destroy()
                event.set()
                
            dialog.protocol("WM_DELETE_WINDOW", lambda: handle_result(False))
                
            btn_approve = customtkinter.CTkButton(btn_frame, text="✅ Approve", fg_color="#107C10", hover_color="#0E6B0E", command=lambda: handle_result(True))
            btn_approve.pack(side="left", padx=10, expand=True)
            
            btn_deny = customtkinter.CTkButton(btn_frame, text="❌ Deny", fg_color="#D13438", hover_color="#B71C1C", command=lambda: handle_result(False))
            btn_deny.pack(side="right", padx=10, expand=True)

        self.after(0, show_dialog)
        event.wait()
        
        return result_container[0] if result_container else False

    def _reset_ui(self):
        self.is_running = False
        self.action_btn.configure(state="normal", text="🚀 Start Agent", fg_color="#107C10")
        self.goal_entry.configure(state="normal")
        self.goal_entry.delete(0, "end")

    def _add_trace_item(self, event_type, message):
        """Add a visual item to the trace view."""
        
        # Style config
        colors = {
            "thinking": ("#666666", "#999999"), # Gray
            "thought":  ("#333333", "#E0E0E0"), # Normal Text
            "tool":     ("#007ACC", "#4A9EFF"), # Blue
            "answer":   ("#107C10", "#6CC45E"), # Green
            "error":    ("#D13438", "#F48771"), # Red
            "user":     ("#000000", "#FFFFFF"), # Bold
            "system":   ("#888888", "#888888"),
            "separator":("#CCCCCC", "#444444")
        }
        
        icon = {
            "thinking": "🤔",
            "thought": "💭",
            "tool": "🛠️",
            "answer": "✅",
            "error": "❌",
            "user": "👤",
            "system": "ℹ️",
            "separator": ""
        }
        
        evt = event_type.lower()
        color = colors.get(evt, colors["thought"])
        prefix = icon.get(evt, "")
        
        if evt == "separator":
            sep = customtkinter.CTkFrame(self.trace_view, height=2, fg_color=color)
            sep.pack(fill="x", padx=10, pady=10)
            return

        # Container
        item_frame = customtkinter.CTkFrame(self.trace_view, fg_color="transparent")
        item_frame.pack(fill="x", padx=5, pady=2)
        
        if evt == "tool":
            # Special formatting for tool calls (monospaced look)
            lbl = customtkinter.CTkLabel(
                item_frame, 
                text=f"{prefix} {message}", 
                text_color=color, 
                font=("Consolas", 11),
                anchor="w", justify="left", wraplength=280
            )
            lbl.pack(fill="x")
        else:
            # Normal text
            font = ("Segoe UI", 12)
            if evt == "user" or evt == "answer":
                font = ("Segoe UI", 12, "bold")
                
            lbl = customtkinter.CTkLabel(
                item_frame,
                text=f"{prefix} {message}",
                text_color=color,
                font=font,
                anchor="w", justify="left", wraplength=280
            )
            lbl.pack(fill="x")

        # Auto-scroll
        try:
            self.trace_view._parent_canvas.yview_moveto(1.0)
        except:
            pass
