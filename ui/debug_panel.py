"""Debug Panel: VS Code-style Run & Debug sidebar panel with breakpoint controls."""
import customtkinter as ctk
import tkinter as tk
from core.debugger.breakpoint_manager import BreakpointManager
from logger import logger


class DebugPanel(ctk.CTkFrame):
    """Debug/Run panel for the sidebar with execution controls and breakpoint list."""

    def __init__(self, master, app):
        super().__init__(master, fg_color=("#F3F3F3", "#252526"), corner_radius=0)
        self.app = app

        # Shared breakpoint manager
        self.bp_manager = BreakpointManager()

        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, height=35, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="RUN AND DEBUG",
            font=("Segoe UI", 11, "bold"),
            text_color=("#383838", "#CCCCCC")
        ).pack(side="left", padx=10, pady=8)

        # ── Run Controls ────────────────────────────────────
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            controls, text="▶ Run Current File",
            command=self._run_file,
            height=32, font=("Segoe UI", 11),
            fg_color=("#007ACC", "#007ACC")
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkButton(
            controls, text="🐛 Debug Current File",
            command=self._debug_file,
            height=32, font=("Segoe UI", 11),
            fg_color=("#6A0DAD", "#6A0DAD"),
            hover_color=("#8B2FC9", "#8B2FC9")
        ).pack(fill="x", pady=(0, 5))

        # Debug step controls (initially disabled)
        step_frame = ctk.CTkFrame(self, fg_color="transparent")
        step_frame.pack(fill="x", padx=10, pady=5)

        self.btn_continue = ctk.CTkButton(
            step_frame, text="▶ Continue", width=75, height=26,
            command=self._debug_continue, font=("Segoe UI", 10),
            state="disabled"
        )
        self.btn_continue.pack(side="left", padx=2)

        self.btn_step_over = ctk.CTkButton(
            step_frame, text="⤵ Over", width=55, height=26,
            command=self._debug_step_over, font=("Segoe UI", 10),
            state="disabled"
        )
        self.btn_step_over.pack(side="left", padx=2)

        self.btn_step_into = ctk.CTkButton(
            step_frame, text="↓ Into", width=50, height=26,
            command=self._debug_step_into, font=("Segoe UI", 10),
            state="disabled"
        )
        self.btn_step_into.pack(side="left", padx=2)

        self.btn_stop = ctk.CTkButton(
            step_frame, text="■ Stop", width=60, height=26,
            command=self._debug_stop, font=("Segoe UI", 10),
            fg_color="#B00020", hover_color="#CF6679",
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=2)

        # ── Divider ─────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=("#D0D0D0", "#3E3E42")).pack(fill="x", pady=5)

        # ── Breakpoints Section ─────────────────────────────
        bp_header = ctk.CTkFrame(self, fg_color="transparent")
        bp_header.pack(fill="x", padx=10)

        ctk.CTkLabel(
            bp_header, text="BREAKPOINTS",
            font=("Segoe UI", 10, "bold"),
            text_color=("#666666", "#999999")
        ).pack(side="left")

        ctk.CTkButton(
            bp_header, text="Clear All", width=60, height=20,
            font=("Segoe UI", 9), fg_color="transparent",
            hover_color=("#D0D0D0", "#404040"),
            command=self._clear_all_breakpoints
        ).pack(side="right")

        self.bp_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.bp_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.no_bp_label = ctk.CTkLabel(
            self.bp_scroll, text="No breakpoints set.",
            text_color=("#666666", "#999999"), font=("Segoe UI", 11)
        )
        self.no_bp_label.pack(pady=20)

        # Listen for breakpoint changes
        self.bp_manager.add_listener(self._on_breakpoint_changed)

        # ── Debug Output ────────────────────────────────────
        out_header = ctk.CTkFrame(self, fg_color="transparent")
        out_header.pack(fill="x", padx=10, pady=(5, 0))
        ctk.CTkLabel(
            out_header, text="DEBUG OUTPUT", font=("Segoe UI", 10, "bold"),
            text_color=("#666666", "#999999")
        ).pack(side="left")

        self.output_text = ctk.CTkTextbox(
            self, height=100, font=("monospace", 10),
            fg_color=("#E5E5E5", "#1E1E1E"), text_color=("#333333", "#D4D4D4"),
            wrap="word", state="disabled"
        )
        self.output_text.pack(fill="x", padx=5, pady=5)

        # Execution controller reference (set externally)
        self.exec_controller = None

    def connect_line_numbers(self, line_numbers, file_path=None):
        """Wire breakpoint manager to line numbers widget."""
        line_numbers.set_breakpoint_manager(self.bp_manager, file_path)

    def _on_breakpoint_changed(self, file_path, line, added):
        """Listener callback: refresh breakpoint display."""
        self._refresh_breakpoints()

    def _refresh_breakpoints(self):
        """Rebuild the breakpoints list UI."""
        for w in self.bp_scroll.winfo_children():
            w.destroy()

        all_bps = self.bp_manager.get_all_breakpoints()

        if not all_bps:
            ctk.CTkLabel(
                self.bp_scroll, text="No breakpoints set.",
                text_color=("#666666", "#999999"), font=("Segoe UI", 11)
            ).pack(pady=20)
            return

        for fp, lines in all_bps.items():
            filename = fp.split('/')[-1]
            for ln in lines:
                row = ctk.CTkFrame(self.bp_scroll, fg_color="transparent", height=22)
                row.pack(fill="x", pady=1)

                # Red dot
                ctk.CTkLabel(
                    row, text="⬤", text_color="#E51400",
                    font=("Segoe UI", 8), width=16
                ).pack(side="left", padx=3)

                # File:line
                ctk.CTkLabel(
                    row, text=f"{filename}:{ln}",
                    font=("Segoe UI", 10), anchor="w"
                ).pack(side="left", fill="x", expand=True)

                # Remove button
                ctk.CTkButton(
                    row, text="✕", width=18, height=18,
                    font=("Segoe UI", 10), fg_color="transparent",
                    hover_color=("#D0D0D0", "#404040"),
                    command=lambda f=fp, l=ln: self._remove_bp(f, l)
                ).pack(side="right", padx=2)

    def _remove_bp(self, fp, ln):
        self.bp_manager.remove_breakpoint(fp, ln)
        # Redraw line numbers if accessible
        if hasattr(self.app, 'tab_manager') and self.app.tab_manager.line_numbers:
            self.app.tab_manager.line_numbers.redraw()

    def _clear_all_breakpoints(self):
        self.bp_manager.clear_all()
        self._refresh_breakpoints()
        if hasattr(self.app, 'tab_manager') and self.app.tab_manager.line_numbers:
            self.app.tab_manager.line_numbers.redraw()

    def _run_file(self):
        """Delegate to app's run_current_file."""
        if hasattr(self.app, 'run_current_file'):
            self.app.run_current_file()

    def _debug_file(self):
        """Start a debug session with current breakpoints."""
        if not self.exec_controller:
            logger.warning("No execution controller configured")
            if hasattr(self.app, 'feedback'):
                self.app.feedback.show_warning("Debug controller not ready")
            return

        tab = self.app.tab_manager.get_current_tab()
        if not tab or not tab.file_path:
            return

        # BUG-2 Fix: Auto-save before debugging
        self.app.save_file()

        bps = self.bp_manager.get_breakpoints(tab.file_path)
        self.exec_controller.start_debug(tab.file_path, bps)
        self._set_debug_buttons(True)

    def _debug_continue(self):
        if self.exec_controller:
            self.exec_controller.send_command("c")

    def _debug_step_over(self):
        if self.exec_controller:
            self.exec_controller.send_command("n")

    def _debug_step_into(self):
        if self.exec_controller:
            self.exec_controller.send_command("s")

    def _debug_stop(self):
        if self.exec_controller:
            self.exec_controller.stop()
            self._set_debug_buttons(False)

    def _set_debug_buttons(self, active: bool):
        """Enable/disable debug step controls."""
        state = "normal" if active else "disabled"
        self.btn_continue.configure(state=state)
        self.btn_step_over.configure(state=state)
        self.btn_step_into.configure(state=state)
        self.btn_stop.configure(state=state)

    def append_output(self, text: str):
        """Append safe text to the debug output panel."""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", text + "\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
