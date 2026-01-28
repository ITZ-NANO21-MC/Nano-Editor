import subprocess
import threading
import queue
import os
import signal
import platform
import time
from typing import Optional

class TerminalProcess:
    """
    Backend logic for managing a terminal subprocess.
    Handles spawning, I/O streaming, and termination.
    """
    def __init__(self, output_queue: queue.Queue):
        self.output_queue = output_queue
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.stdout_thread: Optional[threading.Thread] = None
        self.stderr_thread: Optional[threading.Thread] = None

    def start(self, command: str, cwd: str, shell_path: str) -> None:
        """Start a new terminal process."""
        if self.running:
            self.stop()

        try:
            # Determine shell command based on OS
            if platform.system() == "Windows":
                shell_cmd = ["cmd", "/c", command]
            else:
                shell_cmd = [shell_path, "-c", command]

            # Start process
            self.process = subprocess.Popen(
                shell_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=0,  # Unbuffered for real-time interaction
                universal_newlines=True,
                cwd=cwd,
                env=os.environ.copy()
            )

            self.running = True

            # Start reader threads
            self.stdout_thread = threading.Thread(
                target=self._read_stream, 
                args=(self.process.stdout, "output"), 
                daemon=True
            )
            self.stderr_thread = threading.Thread(
                target=self._read_stream, 
                args=(self.process.stderr, "error"), 
                daemon=True
            )

            self.stdout_thread.start()
            self.stderr_thread.start()

        except Exception as e:
            self.output_queue.put((f"Error starting process: {e}\n", "error"))
            self.running = False
    
    def wait(self) -> int:
        """Wait for process to finish and return exit code."""
        if not self.process:
            return 0
        
        returncode = self.process.wait()
        
        # Signal threads to stop (they should exit on partial read or closed pipe anyway)
        self.running = False
        
        # Wait for threads to finish draining
        if self.stdout_thread:
            self.stdout_thread.join(timeout=1.0)
        if self.stderr_thread:
            self.stderr_thread.join(timeout=1.0)
            
        return returncode

    def stop(self) -> None:
        """Force complete termination of the process."""
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
                self.process = None

    def write(self, input_str: str) -> None:
        """Write input to the process stdin."""
        if self.process and self.running and self.process.stdin:
            try:
                self.process.stdin.write(input_str + "\n")
                self.process.stdin.flush()
            except Exception as e:
                self.output_queue.put((f"Error sending input: {e}\n", "error"))

    def _read_stream(self, stream, tag: str) -> None:
        """Reads from a stream and puts data into the output queue."""
        try:
            while self.running and self.process:
                # Read char by char for real-time updates
                char = stream.read(1)
                if not char:
                    break
                self.output_queue.put((char, tag))
        except Exception:
            pass  # Stream closed or other error
