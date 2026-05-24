"""
Centralized mapping for operation parameter labels.
Ensures consistency between UI, generated reports, and the parser.
"""

from typing import Dict

# Internal key -> Short label (used in UI and Reports)
PARAM_LABELS: Dict[str, str] = {
    "workpiece_diameter": "D",
    "spindle_speed": "S",
    "feed_rate": "F",
    "removal_depth": "TotDepth",
    "cut_depth": "CutDepth",
    "processing_length": "L",
    "drilling_depth": "Depth",
    "peck_depth": "PeckQ",
    "passes_count": "Passes"
}

# Short label -> Internal key (used for parsing)
REVERSE_PARAM_LABELS: Dict[str, str] = {v: k for k, v in PARAM_LABELS.items()}
