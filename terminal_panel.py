"""Integrated terminal panel with advanced features."""
import customtkinter as ctk
import tkinter as tk
import subprocess
import threading
import os
import sys
import signal
import platform
import select
import queue
import time
from typing import Optional, List, Dict, Tuple
from pathlib import Path


class TerminalPanel(ctk.CTkFrame):
    """Advanced integrated terminal with shell-like features."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configuration
        self.shell = self._detect_default_shell()
        self.cwd = os.getcwd()
        self.process = None
        self.process_thread = None
        self.running = False
        self.output_queue = queue.Queue()
        self.command_history = []
        self.history_index = 0
        self.current_command = ""
        
        # ANSI Color mapping
        self.ansi_colors = {
            "30": "black", "31": "error", "32": "success", "33": "command",
            "34": "prompt", "35": "ps1", "36": "directory", "37": "output",
            "90": "output", "91": "error", "92": "success", "93": "command",
            "94": "prompt", "95": "ps1", "96": "directory", "97": "output"
        }
        
        self.colors = {
            "prompt": "#4A9EFF",
            "command": "#FFD700",
            "output": "#CCCCCC",
            "error": "#FF5555",
            "success": "#50FA7B",
            "directory": "#8BE9FD",
            "ps1": "#FF79C6",
            "black": "#000000"
        }
        
        # Shell prompt configuration
        self.prompt = self._get_prompt()
        self.show_prompt = True
        
        # Setup UI
        self._setup_ui()
        
        # Start output processor
        self._start_output_processor()
        
        # Write welcome message
        self._write_welcome()
    
    def _detect_default_shell(self) -> str:
        """Detect the default shell for the system."""
        system = platform.system()
        
        if system == "Windows":
            # Windows - prefer PowerShell if available
            try:
                subprocess.run(["powershell", "-Command", "echo $PSVersionTable"], 
                             capture_output=True, shell=True, timeout=2)
                return "powershell"
            except:
                return "cmd"
        else:
            # Unix-like systems
            shell = os.environ.get("SHELL", "/bin/bash")
            
            # Check if shell exists
            if os.path.exists(shell):
                return shell
            
            # Fallback shells
            for shell_path in ["/bin/bash", "/bin/zsh", "/bin/sh"]:
                if os.path.exists(shell_path):
                    return shell_path
            
            return "/bin/sh"
    
    def _get_prompt(self) -> str:
        """Generate appropriate prompt for the current shell."""
        if "powershell" in self.shell.lower():
            return f"PS {self.cwd}> "
        elif "cmd" in self.shell.lower():
            return f"{self.cwd}> "
        else:
            # Unix-like shells
            try:
                user = os.environ.get("USER", "user")
                hostname = platform.node().split('.')[0]
                return f"{user}@{hostname}:{self.cwd}$ "
            except:
                return f"{self.cwd}$ "
    
    def _setup_ui(self):
        """Setup terminal UI components."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Output text area with scrollbar
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        # Text widget for output (using tkinter Text for better performance)
        self.output_text = tk.Text(
            self.output_frame,
            bg="#1E1E1E",
            fg="#CCCCCC",
            font=("Consolas", 11),
            insertbackground="#FFFFFF",
            wrap="word",
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(
            self.output_frame,
            command=self.output_text.yview
        )
        self.output_text.configure(yscrollcommand=self.scrollbar.set)
        
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure tags for colored output
        for name, color in self.colors.items():
            self.output_text.tag_config(name, foreground=color)
        
        # Configure text widget to look like CTk
        self.output_text.configure(
            selectbackground="#3B8ED0",
            selectforeground="#FFFFFF",
            inactiveselectbackground="#3B8ED0"
        )
        
        # Input frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Command input with history support
        self.cmd_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type command here...",
            font=("Consolas", 11)
        )
        self.cmd_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Bind keys
        self.cmd_input.bind("<Return>", self._on_command_enter)
        self.cmd_input.bind("<Up>", self._history_up)
        self.cmd_input.bind("<Down>", self._history_down)
        self.cmd_input.bind("<Tab>", self._tab_completion)
        self.cmd_input.bind("<Control-c>", self._send_ctrl_c)
        self.cmd_input.bind("<Control-l>", self._clear_screen)
        self.cmd_input.bind("<Control-d>", self._on_ctrl_d)
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.button_frame.grid(row=0, column=1, sticky="e")
        
        # Buttons
        self.run_btn = ctk.CTkButton(
            self.button_frame, 
            text="Run",
            width=60,
            command=self._execute_command_from_input,
            fg_color="#007ACC",
            hover_color="#005A9E"
        )
        self.run_btn.grid(row=0, column=0, padx=2)
        
        self.kill_btn = ctk.CTkButton(
            self.button_frame,
            text="Stop",
            width=60,
            command=self._kill_process,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            state="disabled"
        )
        self.kill_btn.grid(row=0, column=1, padx=2)
        
        self.clear_btn = ctk.CTkButton(
            self.button_frame,
            text="Clear",
            width=60,
            command=self._clear_output,
            fg_color="#666666",
            hover_color="#555555"
        )
        self.clear_btn.grid(row=0, column=2, padx=2)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.input_frame,
            text="Ready",
            text_color="#AAAAAA",
            font=("Segoe UI", 9)
        )
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 0))
    
    def _write_welcome(self):
        """Write welcome message to terminal."""
        welcome = f"""
╔══════════════════════════════════════════════════════════════════════╗
║ NanoEditor Terminal v1.0                                             ║
║ Shell: {self.shell:<25}                                     ║
║ Directory: {self.cwd:<30}             ║
╚══════════════════════════════════════════════════════════════════════╝

Type 'help' for available commands, or start typing commands.

"""
        self._write_to_output(welcome, "prompt")
        
        if self.show_prompt:
            self._write_prompt()
    
    def _write_prompt(self):
        """Write shell prompt."""
        self.prompt = self._get_prompt()
        self._write_to_output(self.prompt, "ps1")
        
        # Move cursor to end
        self.output_text.see("end")
    
    def _write_to_output(self, text: str, tag: str = "output"):
        """Write text to output area directly (used for one-off messages)."""
        self.output_text.configure(state="normal")
        self._write_to_output_raw(text, tag)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
    
    def _start_output_processor(self):
        """Start thread to process output from queue with batching."""
        def processor():
            while True:
                try:
                    # Batch processing to prevent UI lag
                    batch = []
                    # Wait for at least one item
                    try:
                        first_item = self.output_queue.get(timeout=0.1)
                        batch.append(first_item)
                    except queue.Empty:
                        continue
                    
                    # Grab everything currently in queue, up to 1000 items
                    while not self.output_queue.empty() and len(batch) < 1000:
                        try:
                            batch.append(self.output_queue.get_nowait())
                        except queue.Empty:
                            break
                    
                    if batch:
                        # Process the batch as a single UI update if possible
                        # but _write_to_output handles ANSI sequences, so we group by tags
                        self.after(0, lambda b=batch: self._process_batch(b))
                        
                except Exception:
                    break
        
        thread = threading.Thread(target=processor, daemon=True)
        thread.start()

    def _process_batch(self, batch: List[Tuple[str, str]]):
        """Process a batch of output items efficiently."""
        self.output_text.configure(state="normal")
        
        # Optimize: group consecutive items with same tag to reduce insert calls
        if not batch: return
        
        current_text = ""
        current_tag = batch[0][1]
        
        for text, tag in batch:
            if tag == current_tag:
                current_text += text
            else:
                self._write_to_output_raw(current_text, current_tag)
                current_text = text
                current_tag = tag
        
        if current_text:
            self._write_to_output_raw(current_text, current_tag)
            
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def _write_to_output_raw(self, text: str, tag: str):
        """Low-level write to text widget with ANSI support."""
        if "\x1b[" in text:
            import re
            parts = re.split(r'(\x1b\[[0-9;]*m)', text)
            active_tag = tag
            
            for part in parts:
                if part.startswith('\x1b['):
                    match = re.search(r'([0-9]{1,2})m', part)
                    if match:
                        code = match.group(1)
                        if code == "0":
                            active_tag = tag
                        elif code in self.ansi_colors:
                            active_tag = self.ansi_colors[code]
                else:
                    if part:
                        self.output_text.insert("end", part, active_tag)
        else:
            self.output_text.insert("end", text, tag)
    
    def _on_command_enter(self, event=None):
        """Handle Enter key in command input."""
        command = self.cmd_input.get()
        self.cmd_input.delete(0, "end")
        
        # If a process is running, send to stdin
        if self.process and self.running:
            # Display the entered input in terminal
            self._write_to_output(f"{command}\n", "command")
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                self.output_queue.put((f"Error sending input: {e}\n", "error"))
            return

        command = command.strip()
        if not command:
            # Just show a new prompt if empty
            if self.show_prompt:
                 self._write_prompt()
            return
        
        # Add to history
        if not self.command_history or self.command_history[-1] != command:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Display command with prompt
        if self.show_prompt:
            self._write_to_output(f"{command}\n", "command")
        
        # Execute command
        self._execute_command(command)
    
    def _execute_command_from_input(self):
        """Execute command from input field."""
        self._on_command_enter()
    
    def _execute_command(self, command: str):
        """Execute a shell command."""
        # Handle built-in commands
        if self._handle_builtin_commands(command):
            return
        
        # Execute external command
        self._run_external_command(command)
    
    def _handle_builtin_commands(self, command: str) -> bool:
        """Handle built-in terminal commands."""
        cmd_lower = command.strip().lower()
        
        # Clear screen
        if cmd_lower == "clear" or cmd_lower == "cls":
            self._clear_output()
            return True
        
        # Change directory
        elif cmd_lower.startswith("cd "):
            path = command[3:].strip()
            self._change_directory(path)
            return True
        
        # Help command
        elif cmd_lower == "help":
            self._show_help()
            return True
        
        # List directory
        elif cmd_lower == "ls" or cmd_lower.startswith("ls "):
            self._list_directory(command)
            return True
        
        # Print working directory
        elif cmd_lower == "pwd":
            self._write_to_output(f"{self.cwd}\n", "directory")
            if self.show_prompt:
                self._write_prompt()
            return True
        
        # Exit terminal process
        elif cmd_lower == "exit" or cmd_lower == "quit":
            if self.process:
                self._kill_process()
            return True
        
        # Echo command
        elif cmd_lower.startswith("echo "):
            text = command[5:].strip()
            self._write_to_output(f"{text}\n", "output")
            if self.show_prompt:
                self._write_prompt()
            return True
        
        return False
    
    def _run_external_command(self, command: str):
        """Run external command in subprocess."""
        # Update UI state
        self.run_btn.configure(state="disabled")
        self.kill_btn.configure(state="normal")
        self.status_label.configure(text="Running...", text_color="#FFD700")
        
        def run_command():
            try:
                # Determine shell based on OS
                if platform.system() == "Windows":
                    shell_cmd = ["cmd", "/c", command]
                else:
                    shell_cmd = [self.shell, "-c", command]
                
                # Start process
                self.process = subprocess.Popen(
                    shell_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=0, # Unbuffered for real-time interaction
                    universal_newlines=True,
                    cwd=self.cwd,
                    env=os.environ.copy()
                )
                
                self.running = True
                
                # Use separate threads for stdout and stderr to prevent deadlocks
                # and allow reading character by character for interactive prompts
                
                def read_stream(stream, tag):
                    try:
                        # Use a small buffer but allow character by character fallback
                        while self.running and self.process:
                            # Use read(1) for prompts, but we could optimize to read more if available
                            char = stream.read(1)
                            if not char:
                                break
                            self.output_queue.put((char, tag))
                    except Exception:
                        pass

                stdout_thread = threading.Thread(target=read_stream, args=(self.process.stdout, "output"), daemon=True)
                stderr_thread = threading.Thread(target=read_stream, args=(self.process.stderr, "error"), daemon=True)
                
                stdout_thread.start()
                stderr_thread.start()
                
                # Wait for process to end
                returncode = self.process.wait()
                
                # IMPORTANT: Wait for threads to finish draining the streams
                self.running = False # Signal threads to stop after finishing read
                stdout_thread.join(timeout=1.0)
                stderr_thread.join(timeout=1.0)
                
                # Wait for queue to be processed by UI
                # We give it a tiny bit of time or we can check queue explicitly
                while not self.output_queue.empty():
                    time.sleep(0.01)

                # Process completed
                self.after(100, self._process_completed, returncode)
                
            except Exception as e:
                self.output_queue.put((f"Error executing command: {e}\n", "error"))
                self.after(0, self._process_completed, 1)
        
        # Start command thread
        self.process_thread = threading.Thread(target=run_command, daemon=True)
        self.process_thread.start()
    
    def _process_completed(self, returncode: int):
        """Handle process completion."""
        self.process = None
        self.running = False
        self.process_thread = None
        
        # Update UI
        self.run_btn.configure(state="normal")
        self.kill_btn.configure(state="disabled")
        
        if returncode == 0:
            self.status_label.configure(text="Completed successfully", text_color="#50FA7B")
        else:
            self.status_label.configure(text=f"Failed (exit code: {returncode})", text_color="#FF5555")
        
        # Write new prompt
        if self.show_prompt:
            self._write_prompt()
    
    def _kill_process(self):
        """Kill the running process."""
        if self.process and self.running:
            try:
                # Send SIGTERM (Unix) or terminate (Windows)
                if platform.system() == "Windows":
                    self.process.terminate()
                else:
                    self.process.send_signal(signal.SIGTERM)
                
                # Wait a bit, then kill if still running
                time.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
                
                self.output_queue.put(("\nProcess terminated by user\n", "error"))
                
            except Exception as e:
                self.output_queue.put((f"Error terminating process: {e}\n", "error"))
            
            finally:
                self.running = False
                self.after(0, self._process_completed, -1)
    
    def _change_directory(self, path: str):
        """Change working directory."""
        try:
            # Handle special paths
            if path == "~":
                path = os.path.expanduser("~")
            elif path == "-":
                # Go to previous directory (would need to track history)
                self._write_to_output("cd - not implemented yet\n", "error")
                if self.show_prompt:
                    self._write_prompt()
                return
            elif not os.path.isabs(path):
                path = os.path.join(self.cwd, path)
            
            # Resolve and normalize path
            path = os.path.abspath(path)
            
            if os.path.isdir(path):
                self.cwd = path
                self._write_to_output(f"Changed directory to: {self.cwd}\n", "directory")
            else:
                self._write_to_output(f"Directory not found: {path}\n", "error")
        
        except Exception as e:
            self._write_to_output(f"Error changing directory: {e}\n", "error")
        
        # Write prompt
        if self.show_prompt:
            self._write_prompt()
    
    def _list_directory(self, command: str):
        """List directory contents (enhanced ls command)."""
        try:
            # Parse options
            args = command.split()
            show_all = "-a" in args or "--all" in args
            long_format = "-l" in args
            
            # Get target directory
            target_dir = self.cwd
            for arg in args[1:]:
                if not arg.startswith("-"):
                    target_dir = os.path.join(self.cwd, arg)
                    break
            
            target_dir = os.path.abspath(target_dir)
            
            if not os.path.isdir(target_dir):
                self._write_to_output(f"Directory not found: {target_dir}\n", "error")
                return
            
            # List files
            entries = []
            for entry in os.listdir(target_dir):
                if not show_all and entry.startswith("."):
                    continue
                
                entry_path = os.path.join(target_dir, entry)
                stat = os.stat(entry_path)
                
                if long_format:
                    # Format like ls -l
                    import time
                    mode = stat.st_mode
                    size = stat.st_size
                    mtime = time.strftime("%b %d %H:%M", time.localtime(stat.st_mtime))
                    
                    # Determine file type
                    if os.path.isdir(entry_path):
                        entry_type = "d"
                        color = "directory"
                    elif os.path.islink(entry_path):
                        entry_type = "l"
                        color = "success"
                    elif os.access(entry_path, os.X_OK):
                        entry_type = "-"
                        color = "command"
                    else:
                        entry_type = "-"
                        color = "output"
                    
                    entry_str = f"{entry_type} {mode:06o} {stat.st_nlink:3} {stat.st_uid:5} {stat.st_gid:5} {size:8} {mtime} {entry}"
                    entries.append((entry_str, color))
                else:
                    # Simple format
                    color = "directory" if os.path.isdir(entry_path) else "output"
                    entries.append((entry, color))
            
            # Sort entries
            entries.sort(key=lambda x: x[0].lower())
            
            # Display entries
            if long_format:
                self._write_to_output(f"total {len(entries)}\n", "output")
            
            for entry, color in entries:
                self._write_to_output(f"{entry}\n", color)
            
        except Exception as e:
            self._write_to_output(f"Error listing directory: {e}\n", "error")
        
        # Write prompt
        if self.show_prompt:
            self._write_prompt()
    
    def _show_help(self):
        """Show extended help message."""
        help_text = """
╔══════════════════════════════════════════════════════════╗
║                    TERMINAL COMMANDS                     ║
╚══════════════════════════════════════════════════════════╝

BASIC COMMANDS:
  clear, cls           - Clear terminal screen
  cd <directory>       - Change working directory
  ls [options] [path]  - List directory contents
  pwd                  - Print working directory
  help                 - Show this help message
  exit, quit           - Exit terminal session

LS OPTIONS:
  -a, --all           - Show all files including hidden
  -l                  - Use long listing format

FILE OPERATIONS:
  cat <file>          - Display file contents
  cp <src> <dest>     - Copy files
  mv <src> <dest>     - Move/rename files
  rm <file>           - Remove files
  mkdir <dir>         - Create directory
  rmdir <dir>         - Remove directory

PROGRAMMING:
  python <script>     - Run Python script
  pip <command>       - Python package manager
  git <command>       - Version control

SYSTEM:
  ps                  - Show processes
  top, htop           - System monitor
  df, du              - Disk usage
  whoami              - Current user
  uname               - System information

KEYBOARD SHORTCUTS:
  Up/Down             - Command history
  Tab                 - Auto-completion
  Ctrl+C              - Stop current command
  Ctrl+L              - Clear screen
  Ctrl+D              - Exit shell (when idle)

EXAMPLES:
  ls -la              - List all files in detail
  cd ~/projects       - Go to projects directory
  python script.py    - Run Python script
  git status          - Check git repository status
  pip install requests - Install Python package

╔══════════════════════════════════════════════════════════╗
║         Type any shell command to execute it              ║
╚══════════════════════════════════════════════════════════╝

"""
        self._write_to_output(help_text, "prompt")
        
        if self.show_prompt:
            self._write_prompt()
    
    def _history_up(self, event=None):
        """Navigate up in command history."""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.cmd_input.delete(0, "end")
            self.cmd_input.insert(0, self.command_history[self.history_index])
        return "break"
    
    def _history_down(self, event=None):
        """Navigate down in command history."""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_input.delete(0, "end")
            self.cmd_input.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.cmd_input.delete(0, "end")
            self.cmd_input.insert(0, self.current_command)
        return "break"
    
    def _tab_completion(self, event=None):
        """Enhanced tab completion for commands and nested paths."""
        line = self.cmd_input.get()
        if not line: return "break"
        
        # Split by spaces but respect quotes? For now simple split.
        parts = line.split()
        if not parts: return "break"
        
        last_part = parts[-1] if not line.endswith(" ") else ""
        
        completions = []
        
        if len(parts) == 1 and not line.endswith(" "):
            # Command completion
            common_commands = ["cd", "ls", "pwd", "clear", "help", "exit", "quit", 
                              "cat", "cp", "mv", "rm", "mkdir", "rmdir",
                              "python", "pip", "git", "echo"]
            for cmd in common_commands:
                if cmd.startswith(last_part):
                    completions.append(cmd)
        
        # Path completion (always try if there's a last part or it looks like a path)
        try:
            # Determine search dir and prefix
            if "/" in last_part or "\\" in last_part:
                dirname = os.path.dirname(last_part)
                prefix = os.path.basename(last_part)
                search_dir = os.path.join(self.cwd, dirname)
            else:
                dirname = ""
                prefix = last_part
                search_dir = self.cwd
                
            if os.path.isdir(search_dir):
                for item in os.listdir(search_dir):
                    if item.startswith(prefix):
                        # Add dir slash for directories
                        suffix = "/" if os.path.isdir(os.path.join(search_dir, item)) else ""
                        completions.append(os.path.join(dirname, item) + suffix)
        except Exception:
            pass
            
        if completions:
            # Find common prefix
            common = os.path.commonprefix(completions)
            if common and common != last_part:
                # Replace the last part with common prefix
                new_line = line[:line.rfind(last_part)] + common
                self.cmd_input.delete(0, "end")
                self.cmd_input.insert(0, new_line)
            elif len(completions) > 1:
                # Show options
                options = [os.path.basename(c.rstrip("/")) for c in completions]
                self._write_to_output("\n" + "  ".join(options[:20]) + "\n", "output")
                self._write_prompt()
        
        return "break"

    def _on_ctrl_d(self, event=None):
        """Handle Ctrl+D (EOF/Exit)."""
        if not self.cmd_input.get():
            if self.running:
                self._kill_process()
            else:
                self._write_to_output("exit\n", "command")
                # Instead of quitting app, just clear input
                self.cmd_input.delete(0, "end")
        return "break"
    
    def _send_ctrl_c(self, event=None):
        """Send Ctrl+C signal."""
        if self.running:
            self._kill_process()
        else:
            # Clear current input line
            self.cmd_input.delete(0, "end")
            if self.show_prompt:
                self._write_to_output("^C\n", "error")
                self._write_prompt()
        return "break"
    
    def _clear_screen(self, event=None):
        """Clear screen with Ctrl+L."""
        self._clear_output()
        return "break"
    
    def _clear_output(self):
        """Clear terminal output."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        
        # Rewrite welcome
        self._write_welcome()
    
    def run_command(self, command: str):
        """Execute command from external source (API)."""
        if self.show_prompt:
            self._write_to_output(f"{command}\n", "command")
        self._execute_command(command)
    
    def set_working_directory(self, path: str):
        """Set working directory."""
        if os.path.isdir(path):
            self.cwd = os.path.abspath(path)
            self._write_to_output(f"Working directory set to: {self.cwd}\n", "directory")
            if self.show_prompt:
                self._write_prompt()
    
    def clear_terminal(self):
        """Clear terminal (alias)."""
        self._clear_output()
