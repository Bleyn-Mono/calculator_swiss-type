"""
Main application window for the Swiss-type Calculator.
Manages global state, machine configuration, and session data.
"""

import customtkinter as ctk
from typing import Dict, Optional
from core.session_manager import SessionManager
from utils.config_loader import ConfigLoader, MachineConfig
from utils.file_exporter import ReportGenerator, FileExporter
from gui.main_spindle import MainSpindleFrame
from gui.back_spindle import BackSpindleFrame


class App(ctk.CTk):
    """
    Main Application class.
    Following the OOP first principle, it coordinates between UI frames and core logic.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title("Swiss-Type Machining Calculator")
        self.geometry("1100x700")

        # 1. Initialize Data
        self.configs: Dict[str, MachineConfig] = ConfigLoader.load_config()
        self.current_machine_name: Optional[str] = None
        self.current_machine_config: Optional[MachineConfig] = None
        
        self.main_session = SessionManager("Main Spindle")
        self.back_session = SessionManager("Back Spindle")

        # 2. Setup UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configures the main layout and widgets."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Tabview/Content area

        # Top Bar: Machine Selection and Filename
        self.top_bar = ctk.CTkFrame(self)
        self.top_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.top_bar, text="Select Machine:").pack(side="left", padx=5)
        self.machine_selector = ctk.CTkOptionMenu(
            self.top_bar, 
            values=list(self.configs.keys()),
            command=self._on_machine_selected
        )
        self.machine_selector.pack(side="left", padx=5)
        self.machine_selector.set("Select...")

        ctk.CTkLabel(self.top_bar, text="Project Name:").pack(side="left", padx=(20, 5))
        self.filename_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Enter filename...")
        self.filename_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Main Content: Tabs for Spindles
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        self.tab_main = self.tabview.add("Main Spindle")
        self.tab_back = self.tabview.add("Back Spindle")
        
        # Initialize Spindle Frames
        self.main_frame = MainSpindleFrame(self.tab_main, session=self.main_session, get_machine_config=self.get_active_config)
        self.main_frame.pack(fill="both", expand=True)
        
        self.back_frame = BackSpindleFrame(self.tab_back, session=self.back_session, get_machine_config=self.get_active_config)
        self.back_frame.pack(fill="both", expand=True)

        # Bottom Bar: Report Generation
        self.bottom_bar = ctk.CTkFrame(self)
        self.bottom_bar.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        self.generate_btn = ctk.CTkButton(
            self.bottom_bar, 
            text="Generate Report (.txt)", 
            command=self._generate_report,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.generate_btn.pack(side="right", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.bottom_bar, text="Ready")
        self.status_label.pack(side="left", padx=10)

    def _on_machine_selected(self, choice: str) -> None:
        """Callback for machine selection."""
        self.current_machine_name = choice
        self.current_machine_config = self.configs[choice]
        self.status_label.configure(text=f"Selected Machine: {choice}")

    def get_active_config(self) -> Optional[MachineConfig]:
        """Returns the currently selected machine configuration."""
        return self.current_machine_config

    def _generate_report(self) -> None:
        """Aggregates data and exports the report."""
        if not self.current_machine_name or not self.current_machine_config:
            self.status_label.configure(text="Error: Please select a machine first!", text_color="red")
            return

        filename = self.filename_entry.get().strip()
        if not filename:
            filename = "Unnamed_Project"

        # 1. Generate Content
        content = ReportGenerator.generate_content(
            machine_name=self.current_machine_name,
            machine_config=self.current_machine_config,
            main_results=self.main_session.get_results(),
            back_results=self.back_session.get_results(),
            filename=filename
        )

        # 2. Save to File
        try:
            path = FileExporter.save_to_txt(content, filename)
            self.status_label.configure(text=f"Report saved to: {path}", text_color="white")
        except Exception as e:
            self.status_label.configure(text=f"Error saving report: {str(e)}", text_color="red")
