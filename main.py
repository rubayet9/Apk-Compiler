"""
APK Compiler - Entry Point
A desktop application to convert web apps and native projects into installable Android APK files.

Author: APK Compiler Team
Version: 1.0.0
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging for stdout and stderr (critical for frozen .exe with console=False)
log_dir = os.path.join(os.path.expanduser("~"), ".apkcompiler")
os.makedirs(log_dir, exist_ok=True)
try:
    stderr_path = os.path.join(log_dir, "app_stderr.log")
    stdout_path = os.path.join(log_dir, "app_stdout.log")
    sys.stderr = open(stderr_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = open(stdout_path, "a", encoding="utf-8", buffering=1)
except Exception:
    pass


def _setup_tkinter_exception_handler():
    """Hook into Tkinter's callback exception reporting so errors don't vanish silently."""
    import tkinter as tk
    import customtkinter as ctk

    def handle_callback_exception(self, exc, val, tb):
        import traceback
        err_msg = "".join(traceback.format_exception(exc, val, tb))
        try:
            with open(os.path.join(log_dir, "app_stderr.log"), "a", encoding="utf-8") as f:
                from datetime import datetime
                f.write(f"\n=== Tkinter Exception at {datetime.now()} ===\n{err_msg}\n")
        except Exception:
            pass

        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Application Error",
                f"An unexpected error occurred:\n\n{val}\n\nDetailed error log: ~/.apkcompiler/app_stderr.log"
            )
        except Exception:
            pass

    tk.Tk.report_callback_exception = handle_callback_exception
    ctk.CTk.report_callback_exception = handle_callback_exception


def main():
    """Launch the APK Compiler application."""
    _setup_tkinter_exception_handler()

    try:
        from src.app import APKBuilderApp
        from src.ui.main_window import MainWindow

        # Create app controller
        app = APKBuilderApp()

        # Create and run the main window
        window = MainWindow(app)
        app.main_window = window

        # Start the application
        window.mainloop()

    except ImportError as e:
        crash_msg = f"Missing dependency: {e}\nPlease run: pip install -r requirements.txt"
        _log_and_show_crash(crash_msg)
        sys.exit(1)
    except Exception as e:
        import traceback
        crash_msg = f"Fatal error: {e}\n\n{traceback.format_exc()}"
        _log_and_show_crash(crash_msg)
        sys.exit(1)


def _log_and_show_crash(msg: str):
    """Log crash to disk and show GUI dialog."""
    crash_dir = os.path.join(os.path.expanduser("~"), ".apkcompiler")
    os.makedirs(crash_dir, exist_ok=True)
    crash_file = os.path.join(crash_dir, "crash.log")
    try:
        with open(crash_file, "a", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"\n=== Crash at {datetime.now()} ===\n{msg}\n")
    except Exception:
        pass

    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("APK Compiler - Error", msg)
        root.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    main()

