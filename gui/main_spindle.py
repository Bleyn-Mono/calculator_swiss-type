"""
UI Frame for the Main Spindle operations.
"""

import customtkinter as ctk
from pathlib import Path
from PIL import Image
from typing import Callable, Optional, Dict, Any
from core.session_manager import SessionManager
from utils.config_loader import MachineConfig
from core.operations import (
    FacingOp, TurningOp, MillingOp, DrillingG1Op, 
    DrillingQOp, WhirlingOp, ThreadingOp
)
from utils.labels import PARAM_LABELS
from core.specific_calc import (
    FacingCalculator, TurningCalculator, MillingCalculator, DrillingG1Calculator,
    DrillingQCalculator, WhirlingCalculator, ThreadingCalculator
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
        self.editing_index: Optional[int] = None
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Sets up the vertical layout: Inputs on top, Results on bottom."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Input area (fixed height)
        self.grid_rowconfigure(1, weight=1) # Results area (expandable)

        # 1. Input Area (Top)
        self.input_container = ctk.CTkFrame(self)
        self.input_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.input_container, text="Main Spindle", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Operation Type Selection Row
        op_type_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        op_type_frame.pack(pady=2)
        
        ctk.CTkLabel(op_type_frame, text="Operation Type:").pack(side="left", padx=5)
        self.op_type_var = ctk.StringVar(value="Facing")
        self.op_selector = ctk.CTkOptionMenu(
            op_type_frame, 
            values=["Facing", "Turning", "Milling", "Drilling (G1)", "Drilling (Q)", "Whirling", "Threading"],
            variable=self.op_type_var,
            command=self._update_fields
        )
        self.op_selector.pack(side="left", padx=5)

        # Dynamic Fields Container
        self.fields_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        self.fields_frame.pack(fill="x", padx=20, pady=2)
        self.entries: Dict[str, ctk.CTkEntry] = {}
        
        self.status_label = ctk.CTkLabel(self.input_container, text="", text_color="red")
        self.status_label.pack(pady=0)
        
        self._update_fields("Facing")

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
        for i in range(5):
            self.fields_frame.grid_columnconfigure(i, weight=0) # Changed to 5 columns

        fields = field_configs.get(op_type, [])
        for i, (key, label) in enumerate(fields):
            row = i // 5 * 2
            col = i % 5
            # Added pady=(2, 0) to avoid cutoff
            ctk.CTkLabel(self.fields_frame, text=label, font=("Arial", 11)).grid(row=row, column=col, padx=5, pady=(2, 0), sticky="w")
            entry = ctk.CTkEntry(self.fields_frame, height=28, width=70) # Fixed small width
            entry.grid(row=row+1, column=col, padx=5, pady=(0, 2), sticky="w") # Sticky west instead of ew
            self.entries[key] = entry

        # Comment field and Calculate button - Compacted
        next_row = (len(fields) - 1) // 5 * 2 + 2
        
        self.comment_entry = ctk.CTkEntry(self.fields_frame, placeholder_text="Enter optional comment...", height=28)
        self.comment_entry.grid(row=next_row, column=0, columnspan=4, padx=5, pady=(5, 2), sticky="ew")
        
        self.add_btn = ctk.CTkButton(
            self.fields_frame, 
            text="Update" if self.editing_index is not None else "Calculate", 
            command=self._add_operation,
            width=80,
            height=28,
            fg_color="#228822" if self.editing_index is not None else "#1f6aa5",
            hover_color="#1a631a" if self.editing_index is not None else "#144e75"
        )
        self.add_btn.grid(row=next_row, column=4, padx=5, pady=(5, 2), sticky="e")


    def _add_operation(self) -> None:
        """Validates input, calculates time, and adds or updates session."""
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
            
            if self.editing_index is not None:
                self.session.update_result(self.editing_index, op_type, time_min, res_data)
                self.status_label.configure(text="Updated successfully!", text_color="green")
                self.editing_index = None
            else:
                self.session.add_result(op_type, time_min, res_data)
                self.status_label.configure(text="Added successfully!", text_color="green")
            
            self._refresh_results()
            self._update_fields(self.op_type_var.get()) # Reset fields and button text
            self.comment_entry.delete(0, 'end')
            
        except ValueError:
            self.status_label.configure(text="Error: Invalid numeric input", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def _refresh_results(self) -> None:
        """Updates the results frame with styled operation blocks including icons."""
        # Clear existing rows
        for widget in self.results_list_frame.winfo_children():
            widget.destroy()
        
        for i, res in enumerate(self.session.get_results()):
            # Main block for the operation
            is_editing = (self.editing_index == i)
            bg_color = "#505050" if is_editing else "#404040"
            border_color = "#228822" if is_editing else "#404040"
            
            block = ctk.CTkFrame(
                self.results_list_frame, 
                fg_color=bg_color, 
                border_color=border_color,
                border_width=2 if is_editing else 0,
                corner_radius=6
            )
            block.pack(fill="x", pady=4, padx=5)
            
            # Make the entire block clickable for editing
            block.bind("<Button-1>", lambda e, idx=i: self._load_operation_to_edit(idx))

            # Icon and Content layout
            content_row = ctk.CTkFrame(block, fg_color="transparent")
            content_row.pack(fill="x", padx=5, pady=5)
            content_row.bind("<Button-1>", lambda e, idx=i: self._load_operation_to_edit(idx))
            
            # 1. Icon (Left side)
            op_name = res['operation']
            icon_path = Path("assets") / "icons" / f"{op_name}.png"
            
            if icon_path.exists():
                try:
                    img = Image.open(icon_path)
                    ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(45, 45))
                    icon_label = ctk.CTkLabel(content_row, image=ctk_image, text="")
                    icon_label.pack(side="left", padx=(5, 10))
                    icon_label.bind("<Button-1>", lambda e, idx=i: self._load_operation_to_edit(idx))
                except Exception:
                    pass

            # 2. Text Content (Right of icon)
            text_container = ctk.CTkFrame(content_row, fg_color="transparent")
            text_container.pack(side="left", fill="both", expand=True)
            text_container.bind("<Button-1>", lambda e, idx=i: self._load_operation_to_edit(idx))
            
            # Comment
            comment = res["details"].get("comment", "")
            if comment:
                comment_label = ctk.CTkLabel(
                    text_container, 
                    text=f"💬 {comment}", 
                    font=("Arial", 11, "italic"), 
                    text_color="#AAAAAA",
                    wraplength=400,
                    justify="left",
                    anchor="w"
                )
                comment_label.pack(fill="x", side="top", padx=2, pady=(0, 2))
                comment_label.bind("<Button-1>", lambda e, idx=i: self._load_operation_to_edit(idx))

            # Top row: Type, Params | Time, Delete
            header_row = ctk.CTkFrame(text_container, fg_color="transparent")
            header_row.pack(fill="x", side="top")
            header_row.bind("<Button-1>", lambda e, idx=i: self._load_operation_to_edit(idx))
            
            # Format parameters string
            params = []
            for k, v in res["details"].items():
                if k != "comment":
                    label = PARAM_LABELS.get(k, k)
                    params.append(f"{label}{v:g}")
            params_str = " ".join(params)
            
            label_text = f"{i+1}. {op_name} ({params_str}) | {res['time_min']:.2f} min"
            info_label = ctk.CTkLabel(header_row, text=label_text, font=("Arial", 12, "bold"))
            info_label.pack(side="left")
            info_label.bind("<Button-1>", lambda e, idx=i: self._load_operation_to_edit(idx))
            
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
            
        self.total_time_label.configure(text=f"TOTAL TIME: {self.session.get_total_time():.2f} min")

    def _load_operation_to_edit(self, index: int) -> None:
        """Loads an existing operation into the input fields for editing."""
        res = self.session.get_results()[index]
        self.editing_index = index
        
        # 1. Set operation type (this will trigger _update_fields)
        self.op_type_var.set(res["operation"])
        self._update_fields(res["operation"])
        
        # 2. Fill parameter fields
        for key, value in res["details"].items():
            if key in self.entries:
                self.entries[key].delete(0, 'end')
                self.entries[key].insert(0, str(value))
        
        # 3. Fill comment
        if "comment" in res["details"]:
            self.comment_entry.delete(0, 'end')
            self.comment_entry.insert(0, res["details"]["comment"])
            
        self.status_label.configure(text=f"Editing operation #{index+1}", text_color="orange")
        self._refresh_results() # Refresh to show selection highlight

    def _delete_operation(self, index: int) -> None:
        """Removes an operation from the session and refreshes the view."""
        if self.editing_index == index:
            self.editing_index = None
            self._update_fields(self.op_type_var.get())
            
        self.session.remove_result(index)
        self._refresh_results()
        self.status_label.configure(text="Deleted successfully!", text_color="orange")

