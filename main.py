"""
Main entry point for the Swiss-type Calculator application.
"""

import customtkinter as ctk
from gui.app import App

def main():
    """Initializes and runs the main application."""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
