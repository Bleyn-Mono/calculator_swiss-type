"""
UI Frame for the Back Spindle operations.
"""

import customtkinter as ctk
from pathlib import Path
from PIL import Image
from typing import Callable, Optional, Dict, Any
from core.session_manager import SessionManager
from utils.config_loader import MachineConfig
from gui.components import MathEntry, ArcLengthDialog
from core.operations import (
    FacingOp, TurningOp, MillingOp, DrillingG1Op, 
    DrillingQOp, WhirlingOp, ThreadingOp, BroachOp
)
from utils.labels import PARAM_LABELS
from core.specific_calc import (
    FacingCalculator, TurningCalculator, MillingCalculator, DrillingG1Calculator,
    DrillingQCalculator, WhirlingCalculator, ThreadingCalculator, BroachCalculator
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
        self.editing_index: Optional[int] = None
        self.last_focused_entry: Optional[MathEntry] = None
        
        # Drag-and-drop state
        self.dragged_item_index: Optional[int] = None
        self.drop_target_index: Optional[int] = None
        self.insertion_line: Optional[ctk.CTkFrame] = None
        self.drag_start_y: int = 0
        self.is_dragging: bool = False
        
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
        
        # Operation Type Selection Row
        op_type_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        op_type_frame.pack(pady=2)
        
        ctk.CTkLabel(op_type_frame, text="Operation Type:").pack(side="left", padx=5)
        self.op_type_var = ctk.StringVar(value="Turning")
        self.op_selector = ctk.CTkOptionMenu(
            op_type_frame, 
            values=["Facing", "Turning", "Milling", "Drilling (G1)", "Drilling (Q)", "Whirling", "Threading", "Broach"],
            variable=self.op_type_var,
            command=self._update_fields
        )
        self.op_selector.pack(side="left", padx=5)

        self.fields_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        self.fields_frame.pack(fill="x", padx=20, pady=2)
        self.entries: Dict[str, ctk.CTkEntry] = {}
        
        self.status_label = ctk.CTkLabel(self.input_container, text="", text_color="red")
        self.status_label.pack(pady=0)
        
        self._update_fields("Turning")

        # 2. Results Area (Bottom)
        self.results_container = ctk.CTkFrame(self)
        self.results_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        ctk.CTkLabel(self.results_container, text="Operation List", font=("Arial", 16, "bold")).pack(pady=5)
        
        self.results_list_frame = ctk.CTkScrollableFrame(self.results_container)
        self.results_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        self.total_time_label = ctk.CTkLabel(self.results_container, text="TOTAL TIME: 0.00 min", font=("Arial", 14, "bold"))
        self.total_time_label.pack(pady=5)

        # 3. Floating/Helper Buttons
        self._setup_helpers()

    def _setup_helpers(self) -> None:
        """Adds utility buttons like Arc Length Calculator."""
        helper_frame = ctk.CTkFrame(self.input_container, fg_color="transparent")
        helper_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        self.arc_btn = ctk.CTkButton(
            helper_frame, 
            text="📏 Arc", 
            width=50, 
            height=24, 
            font=("Arial", 11),
            command=self._open_arc_calculator
        )
        self.arc_btn.pack()

    def _open_arc_calculator(self) -> None:
        """Opens the arc length dialog."""
        ArcLengthDialog(self, on_insert_callback=self._insert_arc_result)

    def _insert_arc_result(self, result: float) -> None:
        """Inserts the calculated result into the last focused entry."""
        if self.last_focused_entry:
            self.last_focused_entry.delete(0, 'end')
            self.last_focused_entry.insert(0, f"{result:.4f}")
            self.status_label.configure(text=f"Inserted arc length: {result:.4f}", text_color="green")
        else:
            self.status_label.configure(text="Error: Select a field first!", text_color="red")

    def _on_entry_focus(self, entry: MathEntry) -> None:
        """Callback for when a MathEntry gains focus."""
        self.last_focused_entry = entry

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
            ],
            "Broach": [
                ("removal_depth", "Tot Dpth (mm)"),
                ("cut_depth", "Cut Dpth (mm)"),
                ("processing_length", "Length (mm)"),
                ("feed_rate", "Feed (min)")
            ]
        }

        # Grid configuration for compact layout
        for i in range(5):
            self.fields_frame.grid_columnconfigure(i, weight=0)

        fields = field_configs.get(op_type, [])
        for i, (key, label) in enumerate(fields):
            row = i // 5 * 2
            col = i % 5
            # Added pady=(2, 0) to avoid cutoff
            ctk.CTkLabel(self.fields_frame, text=label, font=("Arial", 11)).grid(row=row, column=col, padx=5, pady=(2, 0), sticky="w")
            entry = MathEntry(self.fields_frame, height=28, width=70, on_focus_callback=self._on_entry_focus) # Changed to MathEntry
            entry.grid(row=row+1, column=col, padx=5, pady=(0, 2), sticky="w")
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
            elif op_type == "Broach":
                op = BroachOp(**data, comment=comment)
                time_min = BroachCalculator.calculate(op, machine_config)

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
        
        results = self.session.get_results()
        for i, res in enumerate(results):
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
            
            # Event bindings for drag-and-drop and editing
            block.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(e, idx))
            block.bind("<B1-Motion>", self._on_drag_motion)
            block.bind("<ButtonRelease-1>", self._on_drag_stop)

            # Icon and Content layout
            content_row = ctk.CTkFrame(block, fg_color="transparent")
            content_row.pack(fill="x", padx=5, pady=5)
            # Propagate bindings to internal widgets
            for w in [content_row]:
                w.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(e, idx))
                w.bind("<B1-Motion>", self._on_drag_motion)
                w.bind("<ButtonRelease-1>", self._on_drag_stop)
            
            # 1. Icon (Left side)
            op_name = res['operation']
            icon_path = Path("assets") / "icons" / f"{op_name}.png"
            
            if icon_path.exists():
                try:
                    img = Image.open(icon_path)
                    ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(45, 45))
                    icon_label = ctk.CTkLabel(content_row, image=ctk_image, text="")
                    icon_label.pack(side="left", padx=(5, 10))
                    icon_label.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(e, idx))
                    icon_label.bind("<B1-Motion>", self._on_drag_motion)
                    icon_label.bind("<ButtonRelease-1>", self._on_drag_stop)
                except Exception:
                    pass

            # 2. Text Content (Right of icon)
            text_container = ctk.CTkFrame(content_row, fg_color="transparent")
            text_container.pack(side="left", fill="both", expand=True)
            text_container.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(e, idx))
            text_container.bind("<B1-Motion>", self._on_drag_motion)
            text_container.bind("<ButtonRelease-1>", self._on_drag_stop)
            
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
                comment_label.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(e, idx))
                comment_label.bind("<B1-Motion>", self._on_drag_motion)
                comment_label.bind("<ButtonRelease-1>", self._on_drag_stop)

            # Top row: Type, Params | Time, Delete
            header_row = ctk.CTkFrame(text_container, fg_color="transparent")
            header_row.pack(fill="x", side="top")
            header_row.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(e, idx))
            header_row.bind("<B1-Motion>", self._on_drag_motion)
            header_row.bind("<ButtonRelease-1>", self._on_drag_stop)
            
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
            info_label.bind("<Button-1>", lambda e, idx=i: self._on_drag_start(e, idx))
            info_label.bind("<B1-Motion>", self._on_drag_motion)
            info_label.bind("<ButtonRelease-1>", self._on_drag_stop)
            
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

    def _on_drag_start(self, event: Any, index: int) -> None:
        """Initializes drag-and-drop state."""
        self.dragged_item_index = index
        self.drag_start_y = event.y_root
        self.is_dragging = False

    def _on_drag_motion(self, event: Any) -> None:
        """Handles mouse movement during drag."""
        if self.dragged_item_index is None:
            return

        # Start dragging only after moving 5 pixels to distinguish from click
        if not self.is_dragging and abs(event.y_root - self.drag_start_y) > 5:
            self.is_dragging = True
            if self.insertion_line is None:
                self.insertion_line = ctk.CTkFrame(self.results_list_frame, fg_color="#3a7ebf", height=4)

        if self.is_dragging and self.insertion_line and self.insertion_line.winfo_exists():
            # Find the target index based on mouse position
            try:
                y_in_scrollable = event.y_root - self.results_list_frame.winfo_rooty()
                
                widgets = self.results_list_frame.winfo_children()
                # Filter out the insertion line itself and non-existing widgets
                blocks = [w for w in widgets if w != self.insertion_line and w.winfo_exists()]
                
                target_idx = len(blocks)
                for i, block in enumerate(blocks):
                    block_mid_y = block.winfo_y() + block.winfo_height() / 2
                    if y_in_scrollable < block_mid_y:
                        target_idx = i
                        break
                
                self.drop_target_index = target_idx
                
                # Update insertion line position
                if target_idx < len(blocks):
                    # Place line BEFORE target_idx block
                    self.insertion_line.pack_forget()
                    self.insertion_line.pack(fill="x", pady=2, before=blocks[target_idx])
                else:
                    # Place line at the end
                    self.insertion_line.pack_forget()
                    self.insertion_line.pack(fill="x", pady=2)
            except Exception:
                pass # Prevent crash during rapid UI updates

    def _on_drag_stop(self, event: Any) -> None:
        """Finalizes drag-and-drop or handles click for editing."""
        if self.dragged_item_index is None:
            return

        if self.is_dragging:
            # Handle drop
            old_idx = self.dragged_item_index
            new_idx = self.drop_target_index
            
            # If new_idx is same as old or old+1, no move is needed
            # (because inserting at old or old+1 results in the same position)
            if new_idx is not None and new_idx != old_idx and new_idx != old_idx + 1:
                # Actual target index for insert is new_idx
                # But if we are moving downwards, the index shifts after pop
                actual_new_idx = new_idx
                if new_idx > old_idx:
                    actual_new_idx -= 1
                
                # 1. Update editing index if it was moved
                if self.editing_index is not None:
                    if self.editing_index == old_idx:
                        self.editing_index = actual_new_idx
                    elif old_idx < self.editing_index <= actual_new_idx:
                        self.editing_index -= 1
                    elif actual_new_idx <= self.editing_index < old_idx:
                        self.editing_index += 1
                
                # 2. Physical move in session
                self.session.move_result(old_idx, actual_new_idx)
                self.status_label.configure(text=f"Moved operation from {old_idx+1} to {actual_new_idx+1}", text_color="green")
            
            if self.insertion_line:
                try:
                    self.insertion_line.destroy()
                except Exception:
                    pass
                self.insertion_line = None
            
            self._refresh_results()
        else:
            # Handle click (Editing)
            self._load_operation_to_edit(self.dragged_item_index)

        # Reset state
        self.dragged_item_index = None
        self.drop_target_index = None
        self.is_dragging = False

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
