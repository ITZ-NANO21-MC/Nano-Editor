"""Integrated terminal panel."""
import customtkinter
import tkinter
import subprocess
import threading
import os


class TerminalPanel(customtkinter.CTkFrame):
    """Integrated terminal with command execution."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.process = None
        self.cwd = os.getcwd()
        self.interactive_mode = False
        self.input_queue = []
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Output area
        self.output = customtkinter.CTkTextbox(
            self, font=("monospace", 12),
            wrap="word"
        )
        self.output.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Input frame
        input_frame = customtkinter.CTkFrame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Command input
        self.input = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="Enter command..."
        )
        self.input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input.bind("<Return>", lambda e: self.handle_input())
        
        # Run button
        self.run_btn = customtkinter.CTkButton(
            input_frame, text="Run", width=60,
            command=self.execute_command
        )
        self.run_btn.grid(row=0, column=1)
        
        # Clear button
        self.clear_btn = customtkinter.CTkButton(
            input_frame, text="Clear", width=60,
            command=self.clear_output
        )
        self.clear_btn.grid(row=0, column=2, padx=(5, 0))
        
        self.write_output(f"Terminal ready. Working directory: {self.cwd}\n")
        self.write_output("Type 'help' for available commands.\n\n")
    
    def handle_input(self):
        """Handle input from user."""
        text = self.input.get().strip()
        self.input.delete(0, "end")
        
        if self.interactive_mode and self.process:
            # Send input to running process
            self.write_output(f"{text}\n", "input")
            self.input_queue.append(text)
        else:
            # Execute as command
            self.execute_command(text)
    
    def execute_command(self, command=None):
        """Execute command in terminal."""
        if command is None:
            command = self.input.get().strip()
        if not command:
            return
        
        self.write_output(f"$ {command}\n", "command")
        
        # Handle built-in commands
        if command == "clear":
            self.clear_output()
            return
        elif command == "help":
            self.show_help()
            return
        elif command.startswith("cd "):
            self.change_directory(command[3:].strip())
            return
        
        # Execute external command
        self.run_external_command(command)
    
    def run_external_command(self, command):
        """Run external command in subprocess with interactive support."""
        def target():
            try:
                self.run_btn.configure(state="disabled", text="Running...")
                self.interactive_mode = True
                
                self.process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    cwd=self.cwd
                )
                
                # Read output in real-time
                import select
                while self.process.poll() is None:
                    # Check for output
                    if self.process.stdout:
                        line = self.process.stdout.readline()
                        if line:
                            self.write_output(line, "output")
                    
                    # Check for errors
                    if self.process.stderr:
                        line = self.process.stderr.readline()
                        if line:
                            self.write_output(line, "error")
                    
                    # Send queued input
                    while self.input_queue:
                        user_input = self.input_queue.pop(0)
                        self.process.stdin.write(user_input + "\n")
                        self.process.stdin.flush()
                
                # Read remaining output
                stdout, stderr = self.process.communicate()
                if stdout:
                    self.write_output(stdout, "output")
                if stderr:
                    self.write_output(stderr, "error")
                
                if self.process.returncode != 0:
                    self.write_output(f"\nExit code: {self.process.returncode}\n", "error")
                else:
                    self.write_output("\nCompleted successfully.\n", "output")
                
            except Exception as e:
                self.write_output(f"Error: {e}\n", "error")
            finally:
                self.interactive_mode = False
                self.process = None
                self.run_btn.configure(state="normal", text="Run")
                self.write_output("\n")
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
    
    def change_directory(self, path):
        """Change working directory."""
        try:
            if path == "~":
                path = os.path.expanduser("~")
            elif not os.path.isabs(path):
                path = os.path.join(self.cwd, path)
            
            path = os.path.abspath(path)
            
            if os.path.isdir(path):
                self.cwd = path
                self.write_output(f"Changed directory to: {self.cwd}\n", "output")
            else:
                self.write_output(f"Error: Directory not found: {path}\n", "error")
        except Exception as e:
            self.write_output(f"Error: {e}\n", "error")
    
    def show_help(self):
        """Show help message."""
        help_text = """
Available commands:
  clear          - Clear terminal output
  help           - Show this help message
  cd <path>      - Change directory
  
Any other command will be executed in the shell.

Examples:
  python script.py
  ls -la
  git status
  pip install package
"""
        self.write_output(help_text, "output")
    
    def write_output(self, text, tag="normal"):
        """Write text to output area."""
        try:
            self.output.insert("end", text)
            
            # Configure tags for colors
            if tag == "command":
                # Command text in blue
                start = self.output.index("end-1c linestart")
                end = self.output.index("end-1c")
                self.output.tag_add("command", start, end)
                self.output.tag_config("command", foreground="#4A9EFF")
            elif tag == "error":
                # Error text in red
                start = self.output.index("end-1c linestart")
                end = self.output.index("end-1c")
                self.output.tag_add("error", start, end)
                self.output.tag_config("error", foreground="#FF5555")
            
            self.output.see("end")
        except tkinter.TclError:
            pass
    
    def clear_output(self):
        """Clear terminal output."""
        self.output.delete("1.0", "end")
        self.write_output(f"Working directory: {self.cwd}\n\n")
    
    def clear_terminal(self):
        """Alias for clear_output."""
        self.clear_output()
    
    def set_working_directory(self, path):
        """Set working directory from external source."""
        if path and os.path.isdir(path):
            self.cwd = path
            self.write_output(f"Working directory set to: {self.cwd}\n", "output")
