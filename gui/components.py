"""
Custom UI components for the Swiss-type Calculator.
"""

import customtkinter as ctk
import re
from typing import Any

class MathEntry(ctk.CTkEntry):
    """
    A custom Entry widget that evaluates mathematical expressions when Enter is pressed.
    Supports basic operations: +, -, *, /, ., (, ).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Return>", self._evaluate)
        # Store original border color to restore it after showing error
        self._original_border_color = self.cget("border_color")

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
        # Optional: could also play a beep or show a tooltip
