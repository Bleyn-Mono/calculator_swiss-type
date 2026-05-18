"""
UI Frame for the Back Spindle operations.
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from core.session_manager import SessionManager
from utils.config_loader import MachineConfig
from core.operations import (
    FacingOp, TurningOp, MillingOp, DrillingG1Op, 
    DrillingQOp, WhirlingOp, ThreadingOp
)
from core.specific_calc import (
    FacingCalculator, TurningCalculator, MillingCalculator, DrillingG1Calculator,
    DrillingQCalculator, WhirlingCalculator, ThreadingCalculator
)


class BackSpindleFrame(ctk.CTkFrame):
    """
    Handles input and calculation for Back Spindle operations.
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
        """Sets up the vertical layout: Inputs on top, Results on bottom."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Input area
        self.grid_rowconfigure(1, weight=1) # Results area

        # 1. Input Area (Top)
        self.input_container = ctk.CTkFrame(self)
        self.input_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.input_container, text="Back Spindle", font=("Arial", 16, "bold")).pack(pady=5)
        
        ctk.CTkLabel(self.input_container, text="Operation Type:").pack(pady=(5, 0))
        self.op_type_var = ctk.StringVar(value="Turning")
        self.op_selector = ctk.CTkOptionMenu(
            self.input_container, 
            values=["Facing", "Turning", "Milling", "Drilling (G1)", "Drilling (Q)", "Whirling", "Threading"],
            variable=self.op_type_var,
            command=self._update_fields
        )
        self.op_selector.pack(pady=2)

        self.fields_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        self.fields_frame.pack(fill="x", padx=20, pady=5)
        self.entries: Dict[str, ctk.CTkEntry] = {}
        
        self.status_label = ctk.CTkLabel(self.input_container, text="", text_color="red")
        self.status_label.pack(pady=2)
        
        self._update_fields("Turning")

        self.add_btn = ctk.CTkButton(
            self.input_container, 
            text="Calculate & Add", 
            command=self._add_operation
        )
        self.add_btn.pack(pady=5)

        # 2. Results Area (Bottom)
        self.results_container = ctk.CTkFrame(self)
        self.results_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        ctk.CTkLabel(self.results_container, text="Operation List", font=("Arial", 16, "bold")).pack(pady=5)
        
        self.results_list_frame = ctk.CTkScrollableFrame(self.results_container)
        self.results_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        self.total_time_label = ctk.CTkLabel(self.results_container, text="TOTAL TIME: 0.00 min", font=("Arial", 14, "bold"))
        self.total_time_label.pack(pady=5)

    def _update_fields(self, op_type: str) -> None:
        """Dynamically creates input fields based on the selected operation."""
        # Clear existing fields
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        self.status_label.configure(text="")

        field_configs = {
            "Facing": [
                ("workpiece_diameter", "Diam (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Feed (rev)")
            ],
            "Turning": [
                ("removal_depth", "Tot Dpth (mm)"),
                ("cut_depth", "Cut Dpth (mm)"),
                ("processing_length", "Length (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Feed (rev)")
            ],
            "Milling": [
                ("removal_depth", "Tot Dpth (mm)"),
                ("cut_depth", "Cut Dpth (mm)"),
                ("processing_length", "Length (mm)"),
                ("feed_rate", "Feed (min)")
            ],
            "Drilling (G1)": [
                ("drilling_depth", "Depth (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Feed (rev)")
            ],
            "Drilling (Q)": [
                ("drilling_depth", "Depth (mm)"),
                ("peck_depth", "Peck Q (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Feed (rev)")
            ],
            "Whirling": [
                ("processing_length", "Length (mm)"),
                ("feed_rate", "Feed (min)")
            ],
            "Threading": [
                ("workpiece_diameter", "Diam (mm)"),
                ("processing_length", "Length (mm)"),
                ("spindle_speed", "Speed (RPM)"),
                ("feed_rate", "Pitch (rev)"),
                ("passes_count", "Passes")
            ]
        }

        # Grid configuration for compact layout
        for i in range(4):
            self.fields_frame.grid_columnconfigure(i, weight=1)

        fields = field_configs.get(op_type, [])
        for i, (key, label) in enumerate(fields):
            row = i // 4 * 2
            col = i % 4
            ctk.CTkLabel(self.fields_frame, text=label, font=("Arial", 11)).grid(row=row, column=col, padx=5, sticky="w")
            entry = ctk.CTkEntry(self.fields_frame, height=28)
            entry.grid(row=row+1, column=col, padx=5, pady=(0, 5), sticky="ew")
            self.entries[key] = entry

        # Comment field - separate row, full width
        next_row = (len(fields) - 1) // 4 * 2 + 2
        ctk.CTkLabel(self.fields_frame, text="Comment:").grid(row=next_row, column=0, columnspan=4, padx=5, sticky="w")
        self.comment_entry = ctk.CTkEntry(self.fields_frame, placeholder_text="Enter optional comment...")
        self.comment_entry.grid(row=next_row+1, column=0, columnspan=4, padx=5, pady=(0, 5), sticky="ew")

    def _add_operation(self) -> None:
        """Validates input, calculates time, and adds to session."""
        machine_config = self.get_machine_config()
        if not machine_config:
            self.status_label.configure(text="Error: Select machine first!")
            return

        try:
            op_type = self.op_type_var.get()
            # Replace comma with dot to support both formats
            data = {k: float(v.get().replace(',', '.')) for k, v in self.entries.items()}
            comment = self.comment_entry.get().strip()
            
            time_min = 0.0
            if op_type == "Facing":
                op = FacingOp(**data, comment=comment)
                time_min = FacingCalculator.calculate(op, machine_config)
            elif op_type == "Turning":
                op = TurningOp(**data, comment=comment)
                time_min = TurningCalculator.calculate(op, machine_config)
            elif op_type == "Milling":
                op = MillingOp(**data, comment=comment)
                time_min = MillingCalculator.calculate(op, machine_config)
            elif op_type == "Drilling (G1)":
                op = DrillingG1Op(**data, comment=comment)
                time_min = DrillingG1Calculator.calculate(op, machine_config)
            elif op_type == "Drilling (Q)":
                op = DrillingQOp(**data, comment=comment)
                time_min = DrillingQCalculator.calculate(op, machine_config)
            elif op_type == "Whirling":
                op = WhirlingOp(**data, comment=comment)
                time_min = WhirlingCalculator.calculate(op, machine_config)
            elif op_type == "Threading":
                data["passes_count"] = int(data["passes_count"])
                op = ThreadingOp(**data, comment=comment)
                time_min = ThreadingCalculator.calculate(op, machine_config)

            # Store the full operation data including comment
            res_data = data.copy()
            res_data["comment"] = comment
            self.session.add_result(op_type, time_min, res_data)
            
            self._refresh_results()
            self.status_label.configure(text="Added successfully!", text_color="green")
            self.comment_entry.delete(0, 'end') # Clear comment after adding
            
        except ValueError:
            self.status_label.configure(text="Error: Invalid numeric input", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def _refresh_results(self) -> None:
        """Updates the results frame with styled operation blocks."""
        # Clear existing rows
        for widget in self.results_list_frame.winfo_children():
            widget.destroy()
        
        for i, res in enumerate(self.session.get_results()):
            # Main block for the operation
            block = ctk.CTkFrame(self.results_list_frame, fg_color="#333333", corner_radius=6)
            block.pack(fill="x", pady=4, padx=5)
            
            # Top row: Type, Params | Time, Delete
            header_row = ctk.CTkFrame(block, fg_color="transparent")
            header_row.pack(fill="x", padx=10, pady=(5, 0))
            
            # Format parameters string
            params = []
            for k, v in res["details"].items():
                if k != "comment":
                    # Shorten key for display
                    short_k = k.replace("workpiece_", "").replace("processing_", "").replace("spindle_", "").replace("feed_", "F").replace("rate", "").replace("speed", "S").replace("diameter", "D").replace("depth", "H").replace("length", "L").replace("removal_", "Tot").replace("cut_", "Cut")
                    params.append(f"{short_k}{v:g}")
            params_str = " ".join(params)
            
            label_text = f"{i+1}. {res['operation']} ({params_str}) | {res['time_min']:.2f} min"
            ctk.CTkLabel(header_row, text=label_text, font=("Arial", 12, "bold")).pack(side="left")
            
            del_btn = ctk.CTkButton(
                header_row, 
                text="X", 
                width=24, 
                height=24, 
                fg_color="#882222", 
                hover_color="#AA2222",
                command=lambda idx=i: self._delete_operation(idx)
            )
            del_btn.pack(side="right")
            
            # Bottom row: Comment (if exists)
            comment = res["details"].get("comment", "")
            if comment:
                comment_label = ctk.CTkLabel(block, text=f"💬 {comment}", font=("Arial", 11, "italic"), text_color="#AAAAAA")
                comment_label.pack(side="left", padx=15, pady=(0, 5))
            
        self.total_time_label.configure(text=f"TOTAL TIME: {self.session.get_total_time():.2f} min")

    def _delete_operation(self, index: int) -> None:
        """Removes an operation from the session and refreshes the view."""
        self.session.remove_result(index)
        self._refresh_results()
        self.status_label.configure(text="Deleted successfully!", text_color="orange")

    def _delete_operation(self, index: int) -> None:
        """Removes an operation from the session and refreshes the view."""
        self.session.remove_result(index)
        self._refresh_results()
        self.status_label.configure(text="Deleted successfully!", text_color="orange")
