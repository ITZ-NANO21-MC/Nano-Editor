"""Visual feedback system for user actions."""
import customtkinter as ctk
from typing import Optional

class StatusNotification(ctk.CTkFrame):
    """Temporary notification overlay."""
    
    def __init__(self, parent, message: str, type: str = "info"):
        super().__init__(parent, fg_color=self._get_color(type), corner_radius=8)
        
        self.label = ctk.CTkLabel(
            self, text=message,
            font=("Segoe UI", 12),
            text_color="white"
        )
        self.label.pack(padx=15, pady=8)
        
        self.place(relx=0.5, rely=0.9, anchor="center")
        self.after(2000, self.fade_out)
    
    def _get_color(self, type: str) -> str:
        colors = {
            "success": "#28a745",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }
        return colors.get(type, colors["info"])
    
    def fade_out(self):
        self.destroy()

class ProgressIndicator(ctk.CTkFrame):
    """Loading indicator for long operations."""
    
    def __init__(self, parent, message: str = "Processing..."):
        super().__init__(parent, fg_color=("#f0f0f0", "#2b2b2b"), corner_radius=8)
        
        self.label = ctk.CTkLabel(self, text=message, font=("Segoe UI", 12))
        self.label.pack(padx=20, pady=10)
        
        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", width=200)
        self.progress.pack(padx=20, pady=(0, 10))
        self.progress.start()
        
        self.place(relx=0.5, rely=0.5, anchor="center")
    
    def update_message(self, message: str):
        self.label.configure(text=message)
    
    def stop(self):
        self.progress.stop()
        self.destroy()

class VisualFeedback:
    """Manager for visual feedback."""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_notification: Optional[StatusNotification] = None
        self.current_progress: Optional[ProgressIndicator] = None
    
    def show_success(self, message: str):
        self._show_notification(message, "success")
    
    def show_error(self, message: str):
        self._show_notification(message, "error")
    
    def show_warning(self, message: str):
        self._show_notification(message, "warning")
    
    def show_info(self, message: str):
        self._show_notification(message, "info")
    
    def _show_notification(self, message: str, type: str):
        if self.current_notification:
            self.current_notification.destroy()
        self.current_notification = StatusNotification(self.parent, message, type)
    
    def show_progress(self, message: str = "Processing..."):
        if self.current_progress:
            self.current_progress.stop()
        self.current_progress = ProgressIndicator(self.parent, message)
        return self.current_progress
    
    def hide_progress(self):
        if self.current_progress:
            self.current_progress.stop()
            self.current_progress = None
