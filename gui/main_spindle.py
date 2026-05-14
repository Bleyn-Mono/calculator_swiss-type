"""
UI Frame for the Main Spindle operations.
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from core.session_manager import SessionManager
from utils.config_loader import MachineConfig
from core.operations import FacingOp, TurningOp, MillingOp, DrillingG1Op
from core.specific_calc import (
    FacingCalculator, TurningCalculator, MillingCalculator, DrillingG1Calculator
)


class MainSpindleFrame(ctk.CTkFrame):
    """
    Handles input and calculation for Main Spindle operations.
    """

    def __init__(
        self, 
        master: Any, 
        session: SessionManager, 
        get_machine_config: Callable[[], Optional[MachineConfig]]
    ) -> None:
        super().__init__(master)
        self.session = session
        self.get_machine_config = get_machine_config
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Sets up the split layout: Inputs on the left, Results on the right."""
        self.grid_columnconfigure(0, weight=1) # Input area
        self.grid_columnconfigure(1, weight=1) # Results area
        self.grid_rowconfigure(0, weight=1)

        # 1. Input Area
        self.input_container = ctk.CTkFrame(self)
        self.input_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.input_container, text="Add New Operation", font=("Arial", 16, "bold")).pack(pady=10)
        
        ctk.CTkLabel(self.input_container, text="Operation Type:").pack(pady=(10, 0))
        self.op_type_var = ctk.StringVar(value="Facing")
        self.op_selector = ctk.CTkOptionMenu(
            self.input_container, 
            values=["Facing", "Turning", "Milling", "Drilling (G1)"],
            variable=self.op_type_var,
            command=self._update_fields
        )
        self.op_selector.pack(pady=5)

        # Dynamic Fields Container
        self.fields_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        self.fields_frame.pack(fill="x", padx=20, pady=10)
        self.entries: Dict[str, ctk.CTkEntry] = {}
        
        self._update_fields("Facing")

        self.add_btn = ctk.CTkButton(
            self.input_container, 
            text="Calculate & Add", 
            command=self._add_operation
        )
        self.add_btn.pack(pady=20)

        # 2. Results Area
        self.results_container = ctk.CTkFrame(self)
        self.results_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.results_container, text="Operation List", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.results_text = ctk.CTkTextbox(self.results_container, width=400)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_text.configure(state="disabled")

    def _update_fields(self, op_type: str) -> None:
        """Dynamically creates input fields based on the selected operation."""
        # Clear existing fields
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        field_configs = {
            "Facing": [
                ("workpiece_diameter", "Diameter (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Feed (mm/rev)")
            ],
            "Turning": [
                ("removal_depth", "Total Depth (mm)"),
                ("cut_depth", "Cut Depth (mm)"),
                ("processing_length", "Length (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Feed (mm/rev)")
            ],
            "Milling": [
                ("removal_depth", "Total Depth (mm)"),
                ("cut_depth", "Cut Depth (mm)"),
                ("processing_length", "Length (mm)"),
                ("feed_rate", "Feed (mm/min)")
            ],
            "Drilling (G1)": [
                ("drilling_depth", "Depth (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Feed (mm/rev)")
            ]
        }

        for key, label in field_configs.get(op_type, []):
            ctk.CTkLabel(self.fields_frame, text=label).pack(anchor="w")
            entry = ctk.CTkEntry(self.fields_frame)
            entry.pack(fill="x", pady=(0, 5))
            self.entries[key] = entry

    def _add_operation(self) -> None:
        """Validates input, calculates time, and adds to session."""
        machine_config = self.get_machine_config()
        if not machine_config:
            # Should show an error in a real app
            return

        try:
            op_type = self.op_type_var.get()
            data = {k: float(v.get()) for k, v in self.entries.items()}
            
            time_min = 0.0
            if op_type == "Facing":
                op = FacingOp(**data)
                time_min = FacingCalculator.calculate(op, machine_config)
            elif op_type == "Turning":
                op = TurningOp(**data)
                time_min = TurningCalculator.calculate(op, machine_config)
            elif op_type == "Milling":
                op = MillingOp(**data)
                time_min = MillingCalculator.calculate(op, machine_config)
            elif op_type == "Drilling (G1)":
                op = DrillingG1Op(**data)
                time_min = DrillingG1Calculator.calculate(op, machine_config)

            self.session.add_result(op_type, time_min, data)
            self._refresh_results()
            
        except ValueError:
            # Handle invalid input (not a number)
            pass

    def _refresh_results(self) -> None:
        """Updates the text box with the list of operations."""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        
        for i, res in enumerate(self.session.get_results(), 1):
            line = f"{i}. {res['operation']}: {res['time_min']:.2f} min\n"
            self.results_text.insert("end", line)
            
        self.results_text.insert("end", f"\nTOTAL TIME: {self.session.get_total_time():.2f} min")
        self.results_text.configure(state="disabled")
