"""
Main entry point for the Swiss-type Calculator application.
This module bootstraps the application, ensures dependencies are met, and launches the UI.
"""
import sys
from pathlib import Path
import os
import traceback
import time

# Перенаправляем все критические ошибки в текстовый файл
def log_exceptions(exctype, value, tb):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    log_file = os.path.join(desktop, "calculator_error.txt")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("=== КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ ===\n")
        traceback.print_exception(exctype, value, tb, file=f)

sys.excepthook = log_exceptions

# Add project root to sys.path for robust module discovery
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

class AppLauncher:
    """
    Responsible for initializing the environment and starting the GUI application.
    Following the OOP First principle, even the entry point is encapsulated.
    """

    @staticmethod
    def start() -> None:
        """
        Initializes the global UI settings and starts the main application loop.
        
        Raises:
            SystemExit: If required dependencies (customtkinter) are missing.
        """
        # Искусственная пауза перед импортами и инициализацией UI.
        # Дает корпоративному антивирусу время проверить .exe в песочнице
        time.sleep(2.5)
        try:
            import customtkinter as ctk
            from gui.app import App
        except ImportError as e:
            print(f"Critical Error: Missing dependencies. {e}")
            print("To fix this, please run: pip install -r requirements.txt")
            sys.exit(1)
        
        # 1. Configure Global Appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # 2. Launch Application
        try:
            app = App()
            app.mainloop()
        except Exception as e:
            print(f"An unexpected error occurred during execution: {e}")
            sys.exit(1)

if __name__ == "__main__":
    AppLauncher.start()
