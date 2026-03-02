"""ExecutionController: Manages a Pdb debug subprocess.

Wraps Python's pdb module in a subprocess, sends commands (n, c, s, b),
and parses output to determine the current execution line.
"""
import subprocess
import threading
import os
from typing import List, Optional, Callable
from logger import logger


class ExecutionController:
    """Controls a Python debug session via pdb subprocess."""

    def __init__(self, on_output: Optional[Callable[[str], None]] = None,
                 on_line_change: Optional[Callable[[int], None]] = None,
                 on_finished: Optional[Callable[[], None]] = None):
        """Initialize the controller with optional callbacks.
        
        Args:
            on_output: Called with each line of pdb output.
            on_line_change: Called with the current line number when execution pauses.
            on_finished: Called when the debug session ends.
        """
        self.on_output = on_output
        self.on_line_change = on_line_change
        self.on_finished = on_finished
        self._process: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        self._finished_called = False

    @property
    def is_running(self) -> bool:
        return self._running

    def start_debug(self, file_path: str, breakpoints: List[int] = None):
        """Start a pdb debug session for the given file.
        
        Args:
            file_path: Absolute path to the Python file to debug.
            breakpoints: List of line numbers to set as breakpoints.
        """
        if self._running:
            self.stop()

        if not os.path.isfile(file_path):
            logger.error(f"Debug: File not found: {file_path}")
            return

        try:
            self._process = subprocess.Popen(
                ['python3', '-m', 'pdb', file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(file_path)
            )
            self._running = True
            self._finished_called = False
            logger.info(f"Debug session started: {file_path}")

            # Start reader thread
            self._reader_thread = threading.Thread(
                target=self._read_output, daemon=True
            )
            self._reader_thread.start()

            # Inject breakpoints
            if breakpoints:
                for bp_line in breakpoints:
                    self.send_command(f"b {bp_line}")

                # After setting breakpoints, continue to the first one
                self.send_command("c")

        except Exception as e:
            logger.error(f"Failed to start debug session: {e}")
            self._running = False

    def send_command(self, command: str):
        """Send a command to the pdb process (e.g., 'n', 'c', 's', 'b 10')."""
        if not self._process or not self._running:
            return

        try:
            self._process.stdin.write(command + '\n')
            self._process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            logger.error(f"Debug: Failed to send command: {e}")
            self._running = False

    def stop(self):
        """Terminate the debug session."""
        self._running = False

        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=3)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    self._process.kill()
                except OSError:
                    pass
            self._process = None

        logger.info("Debug session stopped")

        if self.on_finished and not self._finished_called:
            self._finished_called = True
            try:
                self.on_finished()
            except Exception:
                pass

    def _read_output(self):
        """Background thread: reads pdb stdout line by line."""
        try:
            while self._running and self._process and self._process.stdout:
                line = self._process.stdout.readline()
                if not line:
                    break

                line = line.rstrip('\n')

                # Notify output listener
                if self.on_output:
                    try:
                        self.on_output(line)
                    except Exception:
                        pass

                # Parse current line indicator from pdb output
                # pdb format: "> /path/to/file.py(LINE)function()"
                #         or: "-> source_line_content"
                if line.startswith('> ') and '(' in line and ')' in line:
                    try:
                        # Extract line number between parentheses
                        start = line.index('(') + 1
                        end = line.index(')')
                        current_line = int(line[start:end])
                        if self.on_line_change:
                            self.on_line_change(current_line)
                    except (ValueError, IndexError):
                        pass

        except Exception as e:
            logger.error(f"Debug reader error: {e}")
        finally:
            self._running = False
            if self.on_finished and not self._finished_called:
                self._finished_called = True
                try:
                    self.on_finished()
                except Exception:
                    pass
