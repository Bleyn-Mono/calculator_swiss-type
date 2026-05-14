"""
This module handles the generation and export of machining reports.
Following the SoC principle, it separates report formatting logic 
(ReportGenerator) from file system operations (FileExporter).
"""

import os
from typing import List, Dict, Any
from utils.config_loader import MachineConfig


class ReportGenerator:
    """
    Aggregates data from different spindles and machine configuration 
    to create a formatted text report.
    """

    @staticmethod
    def format_details(details: Dict[str, Any]) -> str:
        """
        Formats operation-specific parameters into a readable string.
        
        Args:
            details (Dict[str, Any]): Dictionary of cutting parameters.
            
        Returns:
            str: Formatted string of parameters.
        """
        if not details:
            return ""
        
        # Mapping internal keys to readable labels
        labels = {
            "workpiece_diameter": "D",
            "spindle_speed": "S",
            "feed_rate": "F",
            "removal_depth": "Total Depth",
            "cut_depth": "Ap",
            "processing_length": "L",
            "drilling_depth": "Depth",
            "passes_count": "Passes"
        }
        
        parts = []
        for key, value in details.items():
            label = labels.get(key, key.replace("_", " ").capitalize())
            parts.append(f"{label}: {value}")
            
        return " | " + ", ".join(parts)

    @classmethod
    def generate_content(
        self, 
        machine_name: str,
        machine_config: MachineConfig,
        main_results: List[Dict[str, Any]],
        back_results: List[Dict[str, Any]],
        filename: str
    ) -> str:
        """
        Constructs the full text content of the report.
        
        Args:
            machine_name (str): Name of the selected machine.
            machine_config (MachineConfig): Configuration parameters of the machine.
            main_results (List[Dict[str, Any]]): Results from Main Spindle.
            back_results (List[Dict[str, Any]]): Results from Back Spindle.
            filename (str): Name of the output file.
            
        Returns:
            str: Formatted report content.
        """
        lines = []
        lines.append(f"MACHINING CYCLE REPORT: {filename}")
        lines.append(f"MACHINE: {machine_name} ({machine_config.get('description', '')})")
        lines.append("-" * 60)
        lines.append("")

        # Channel 1: Main Spindle
        total_main = sum(res["time_min"] for res in main_results)
        lines.append(f"CHANNEL 1: MAIN SPINDLE")
        for i, res in enumerate(main_results, 1):
            details_str = self.format_details(res.get("details", {}))
            lines.append(f"{i}. {res['operation']}: {res['time_min']:.2f} min{details_str}")
        lines.append(f"TOTAL MAIN TIME: {total_main:.2f} min")
        lines.append("")

        # Channel 2: Back Spindle
        total_back = sum(res["time_min"] for res in back_results)
        lines.append(f"CHANNEL 2: BACK SPINDLE")
        for i, res in enumerate(back_results, 1):
            details_str = self.format_details(res.get("details", {}))
            lines.append(f"{i}. {res['operation']}: {res['time_min']:.2f} min{details_str}")
        lines.append(f"TOTAL BACK TIME: {total_back:.2f} min")
        lines.append("")

        lines.append("-" * 60)
        lines.append("MACHINE SPECIFIC OVERHEAD (Constants):")
        cutoff = machine_config['cutoff_time_s']
        regrip = machine_config['re_grip_time_s']
        ejection = machine_config['ejection_time_s']
        lines.append(f"- Cutoff: {cutoff}s")
        lines.append(f"- Re-grip: {regrip}s")
        lines.append(f"- Ejection: {ejection}s")
        lines.append("")

        # Total Cycle Calculation
        # Cycle = Max(Main, Back) + constants
        overhead_min = (cutoff + regrip + ejection) / 60
        max_spindle_time = max(total_main, total_back)
        total_cycle_min = max_spindle_time + overhead_min
        total_cycle_sec = total_cycle_min * 60

        lines.append("-" * 60)
        lines.append(f"TOTAL CYCLE TIME: {total_cycle_min:.2f} min ({total_cycle_sec:.1f}s)")
        lines.append(f"(Formula: Max(Main, Back) + Overhead)")
        
        return "\n".join(lines)


class FileExporter:
    """
    Handles writing the generated report content to the local file system.
    """

    @staticmethod
    def save_to_txt(content: str, filename: str, output_dir: str = "output") -> str:
        """
        Saves the report content to a .txt file.
        
        Args:
            content (str): The text content to save.
            filename (str): The desired filename (without extension).
            output_dir (str): Directory where the file will be saved.
            
        Returns:
            str: The full path to the saved file.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Ensure filename ends with .txt
        if not filename.endswith(".txt"):
            full_filename = f"{filename}.txt"
        else:
            full_filename = filename

        file_path = os.path.join(output_dir, full_filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return file_path
