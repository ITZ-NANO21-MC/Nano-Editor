"""Diff Viewer: Displays git diffs with syntax highlighting.

Uses a raw tkinter.Text widget instead of CTkTextbox to avoid
CTkTextbox restrictions on tag_config (no font, no color tuples).
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkFont


class DiffViewer(ctk.CTkToplevel):
    """Window to display unified diffs for Git changes."""

    def __init__(self, master, file_path: str, diff_content: str):
        super().__init__(master)
        self.title(f"Diff: {file_path}")
        self.geometry("1000x700")
        self.after(10, self.lift)
        self.minsize(600, 400)

        is_dark = ctk.get_appearance_mode() == "Dark"
        bg = "#1E1E1E" if is_dark else "#FFFFFF"
        fg = "#D4D4D4" if is_dark else "#1E1E1E"

        # ── Header ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, height=40, fg_color=("#E8E8E8", "#2D2D2D"), corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        filename = file_path.split('/')[-1]
        ctk.CTkLabel(
            header, text=f"  Diferencias en: {filename}",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left", padx=10, pady=8)

        ctk.CTkButton(
            header, text="✕ Cerrar", width=90, height=26,
            command=self.destroy, font=("Segoe UI", 11)
        ).pack(side="right", padx=10, pady=7)

        self.stats_label = ctk.CTkLabel(
            header, text="", font=("Segoe UI", 11, "bold")
        )
        self.stats_label.pack(side="right", padx=10, pady=8)

        # ── Line numbers + Text area container ─────────────────
        container = tk.Frame(self, bg=bg)
        container.pack(fill="both", expand=True, padx=8, pady=(5, 8))

        # Line numbers column
        self.line_nums = tk.Text(
            container, width=6, padx=4, pady=4,
            bg="#2D2D2D" if is_dark else "#F0F0F0",
            fg="#858585", font=("monospace", 12),
            state="disabled", relief="flat",
            borderwidth=0, highlightthickness=0,
            cursor="arrow"
        )
        self.line_nums.pack(side="left", fill="y")

        # Scrollbar
        scrollbar = tk.Scrollbar(container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Main text area (raw tkinter.Text for full tag_config control)
        self.text_area = tk.Text(
            container, wrap="none", padx=8, pady=4,
            bg=bg, fg=fg, font=("monospace", 12),
            insertbackground=fg, relief="flat",
            borderwidth=0, highlightthickness=0,
            yscrollcommand=self._on_scroll
        )
        self.text_area.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self._yview)

        # Horizontal scroll
        hscroll = tk.Scrollbar(self, orient="horizontal", command=self.text_area.xview)
        hscroll.pack(fill="x", padx=8)
        self.text_area.config(xscrollcommand=hscroll.set)

        # ── Tag styles ──────────────────────────────────────────
        bold_font = tkFont.Font(family="monospace", size=12, weight="bold")

        self.text_area.tag_config("addition",
            foreground="#00CC44",
            background="#1E3A24" if is_dark else "#E6FFE6")
        self.text_area.tag_config("deletion",
            foreground="#FF4444",
            background="#3A1E1E" if is_dark else "#FFE6E6")
        self.text_area.tag_config("header",
            foreground="#569CD6" if is_dark else "#0066CC",
            font=bold_font)
        self.text_area.tag_config("hunk",
            foreground="#C586C0" if is_dark else "#AF00DB")
        self.text_area.tag_config("context",
            foreground="#858585" if is_dark else "#6A6A6A")

        # Line number tags
        self.line_nums.tag_config("add_ln", foreground="#00CC44")
        self.line_nums.tag_config("del_ln", foreground="#FF4444")

        # ── Render diff ─────────────────────────────────────────
        self._render_diff(diff_content)

        # Make read-only
        self.text_area.config(state="disabled")

    def _on_scroll(self, *args):
        """Sync line numbers with main text scroll."""
        self.line_nums.yview_moveto(args[0])

    def _yview(self, *args):
        """Scroll both text area and line numbers together."""
        self.text_area.yview(*args)
        self.line_nums.yview(*args)

    def _render_diff(self, diff_text: str):
        """Parse raw git diff output and render with colors and line numbers."""
        if not diff_text:
            self.text_area.insert("1.0", "  No hay cambios detectados.\n\n"
                                          "  El archivo puede ser nuevo (untracked)\n"
                                          "  o ya estar staged sin diferencias.")
            return

        self.line_nums.config(state="normal")

        old_ln = 0
        new_ln = 0

        for line in diff_text.split('\n'):
            tag = None
            ln_tag = None
            ln_text = ""

            if line.startswith('diff ') or line.startswith('index '):
                tag = "header"
                ln_text = "  ···"
            elif line.startswith('---') or line.startswith('+++'):
                tag = "header"
                ln_text = "  ···"
            elif line.startswith('@@'):
                tag = "hunk"
                ln_text = "  ···"
                # Parse hunk header: @@ -old,count +new,count @@
                try:
                    parts = line.split(' ')
                    old_ln = abs(int(parts[1].split(',')[0])) - 1
                    new_ln = int(parts[2].split(',')[0]) - 1
                except (IndexError, ValueError):
                    pass
            elif line.startswith('+') and not line.startswith('+++'):
                tag = "addition"
                ln_tag = "add_ln"
                new_ln += 1
                ln_text = f"    +{new_ln}"
            elif line.startswith('-') and not line.startswith('---'):
                tag = "deletion"
                ln_tag = "del_ln"
                old_ln += 1
                ln_text = f"    -{old_ln}"
            else:
                tag = "context"
                old_ln += 1
                new_ln += 1
                ln_text = f" {new_ln:>4}"

            # Insert line content
            self.text_area.insert("end", line + "\n", tag)

            # Insert line number
            if ln_tag:
                self.line_nums.insert("end", ln_text + "\n", ln_tag)
            else:
                self.line_nums.insert("end", ln_text + "\n")

        self.line_nums.config(state="disabled")

        # Compute accurate stats
        adds = sum(1 for line in diff_text.split('\n') if line.startswith('+') and not line.startswith('+++'))
        dels = sum(1 for line in diff_text.split('\n') if line.startswith('-') and not line.startswith('---'))
        self.stats_label.configure(
            text=f"+{adds}   -{dels}",
            text_color=("#00CC44" if adds > 0 else "#666", "#FF4444" if dels > 0 else "#999")
        )
