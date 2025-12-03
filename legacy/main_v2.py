"""Entry point for NanoEditor v2.0 with tabs and terminal."""
import sys
import tkinter

try:
    from editor_view_v2 import App
except ImportError as e:
    print(f"Error: Missing required dependencies.")
    print(f"Details: {e}")
    print("\nPlease install required packages:")
    print("  pip install customtkinter pygments jedi")
    sys.exit(1)


def main():
    try:
        app = App()
        app.mainloop()
    except tkinter.TclError as e:
        print(f"Error: Cannot initialize GUI.")
        print(f"Details: {e}")
        print("\nPossible causes:")
        print("  - No display available (running on server without GUI)")
        print("  - X11 forwarding not configured")
        print("  - Display permissions issue")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: Unexpected error occurred.")
        print(f"Details: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
