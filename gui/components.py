"""
Custom UI components for the Swiss-type Calculator.
"""

import customtkinter as ctk
import re
import math
from typing import Any, Optional, Callable

class MathEntry(ctk.CTkEntry):
    """
    A custom Entry widget that evaluates mathematical expressions when Enter is pressed.
    Supports basic operations: +, -, *, /, ., (, ).
    """

    def __init__(self, *args, on_focus_callback: Optional[Callable[['MathEntry'], None]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_focus_callback = on_focus_callback
        self.bind("<Return>", self._evaluate)
        self.bind("<FocusIn>", self._on_focus)
        # Store original border color to restore it after showing error
        self._original_border_color = self.cget("border_color")

    def _on_focus(self, event: Any) -> None:
        """Called when entry gains focus."""
        if self.on_focus_callback:
            self.on_focus_callback(self)

    def _evaluate(self, event: Any = None) -> None:
        """Evaluates the mathematical expression in the entry."""
        expression = self.get().strip().replace(',', '.')
        if not expression:
            return

        # Regular expression to allow only numbers and math symbols
        # Allowed: 0-9, +, -, *, /, ., (, )
        if not re.fullmatch(r"[0-9+\-*/.() ]+", expression):
            self._show_error()
            return

        try:
            # Use a restricted environment for eval
            result = eval(expression, {"__builtins__": {}}, {})
            
            # Convert to float and format
            result_val = float(result)
            
            # Update the entry with the result
            self.delete(0, 'end')
            self.insert(0, f"{result_val:g}")
            
            # Reset visual state
            self.configure(border_color=self._original_border_color)
            
        except Exception:
            self._show_error()

    def _show_error(self) -> None:
        """Highlights the entry with a red border to indicate an error."""
        self.configure(border_color="red")


class ArcLengthDialog(ctk.CTkToplevel):
    """
    A popup dialog to calculate arc length: L = (pi * D * alpha) / 360.
    """

    def __init__(self, master: Any, on_insert_callback: Callable[[float], None]):
        super().__init__(master)
        self.title("Arc Length Calculator")
        self.geometry("300x200")
        self.on_insert_callback = on_insert_callback
        
        # Make it stay on top
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self._setup_ui()
        
    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Diameter (mm):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.diameter_entry = ctk.CTkEntry(self, width=100)
        self.diameter_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.diameter_entry.insert(0, "0")
        self.diameter_entry.bind("<FocusIn>", lambda e: self._clear_placeholder(self.diameter_entry))

        ctk.CTkLabel(self, text="Angle (deg):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.angle_entry = ctk.CTkEntry(self, width=100)
        self.angle_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.angle_entry.insert(0, "0")
        self.angle_entry.bind("<FocusIn>", lambda e: self._clear_placeholder(self.angle_entry))

        self.calculate_btn = ctk.CTkButton(self, text="Insert Result", command=self._calculate_and_insert)
        self.calculate_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

    def _clear_placeholder(self, entry: ctk.CTkEntry) -> None:
        """Clears the entry if it contains '0' when focused."""
        if entry.get() == "0":
            entry.delete(0, 'end')

    def _calculate_and_insert(self) -> None:
        try:
            d_str = self.diameter_entry.get().replace(',', '.')
            a_str = self.angle_entry.get().replace(',', '.')
            
            d = float(d_str) if d_str else 0.0
            a = float(a_str) if a_str else 0.0
            
            # Formula: L = (pi * D * alpha) / 360
            result = (math.pi * d * a) / 360.0
            
            self.on_insert_callback(result)
            self.destroy()
        except ValueError:
            self.diameter_entry.configure(border_color="red")
            self.angle_entry.configure(border_color="red")
