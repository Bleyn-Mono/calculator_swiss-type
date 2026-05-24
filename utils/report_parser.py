"""
This module implements the logic for parsing .txt reports back into structured data.
Enables the 'Open Project' functionality by reverse-engineering the report format.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from .labels import REVERSE_PARAM_LABELS


class ReportParser:
    """
    Parses generated text reports to reconstruct the application state.
    """

    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Reads a report file and extracts project information.
        
        Returns:
            Dict containing:
                - filename: str
                - machine_name: str
                - main_results: List[Dict]
                - back_results: List[Dict]
        """
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        data = {
            "filename": "Unnamed",
            "machine_name": "",
            "main_results": [],
            "back_results": []
        }

        current_channel = None # 1 for Main, 2 for Back

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 1. Header Extraction
            if line.startswith("MACHINING CYCLE REPORT:"):
                data["filename"] = line.split(":", 1)[1].strip()
                continue
            
            if line.startswith("MACHINE:"):
                # Extract name before the parenthesis
                match = re.search(r"MACHINE:\s*(.*?)\s*\(", line)
                if match:
                    data["machine_name"] = match.group(1).strip()
                else:
                    data["machine_name"] = line.split(":", 1)[1].strip()
                continue

            # 2. Channel Detection
            if "CHANNEL 1: MAIN SPINDLE" in line:
                current_channel = 1
                continue
            elif "CHANNEL 2: BACK SPINDLE" in line:
                current_channel = 2
                continue
            elif "TOTAL MAIN TIME:" in line or "TOTAL BACK TIME:" in line:
                current_channel = None
                continue

            # 3. Operation Parsing
            # Format: "1. Facing: 0.10 min | D: 20, S: 1000, F: 0.1, Comment: test"
            if current_channel and re.match(r"^\d+\.", line):
                op_data = ReportParser._parse_operation_line(line)
                if op_data:
                    if current_channel == 1:
                        data["main_results"].append(op_data)
                    else:
                        data["back_results"].append(op_data)

        return data

    @staticmethod
    def _parse_operation_line(line: str) -> Optional[Dict[str, Any]]:
        """
        Decodes a single operation line into a result dictionary.
        """
        try:
            # Split into: "Number. Name: Time" and "Details"
            parts = line.split(":", 1)
            if len(parts) < 2: return None
            
            # Extract operation name: "1. Facing" -> "Facing"
            op_part = parts[0]
            op_name = re.sub(r"^\d+\.\s*", "", op_part).strip()
            
            # The rest is " Time min | Details"
            rest = parts[1]
            time_match = re.search(r"(\d+\.?\d*)\s*min", rest)
            time_min = float(time_match.group(1)) if time_match else 0.0
            
            details = {}
            if "|" in rest:
                details_str = rest.split("|", 1)[1].strip()
                # Split by comma but ignore commas inside comments if any (though currently they aren't escaped)
                # For now, simple split by ", "
                detail_parts = details_str.split(", ")
                for dp in detail_parts:
                    if ":" in dp:
                        label, val = dp.split(":", 1)
                        label = label.strip()
                        val = val.strip()
                        
                        if label == "Comment":
                            details["comment"] = val
                        elif label in REVERSE_PARAM_LABELS:
                            internal_key = REVERSE_PARAM_LABELS[label]
                            details[internal_key] = float(val)

            return {
                "operation": op_name,
                "time_min": time_min,
                "details": details
            }
        except Exception:
            return None
