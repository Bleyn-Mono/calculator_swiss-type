"""
This module defines data structures (dataclasses) for various machining operations.
Each class represents the input parameters required to calculate the operation time.
"""

from dataclasses import dataclass

@dataclass
class FacingOp:
    """
    Stores parameters for the Facing operation.
    
    Attributes:
        workpiece_diameter (float): Outer diameter of the part in mm.
        spindle_speed (float): Spindle rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
        comment (str): Optional comment.
    """
    workpiece_diameter: float
    spindle_speed: float
    feed_rate: float
    comment: str = ""

@dataclass
class TurningOp:
    """
    Stores parameters for the Turning operation (Longitudinal).
    
    Attributes:
        removal_depth (float): Total material to be removed in mm (radial).
        cut_depth (float): Depth of cut per single pass in mm.
        processing_length (float): Total length of the turning path in mm.
        spindle_speed (float): Spindle rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
        comment (str): Optional comment.
    """
    removal_depth: float
    cut_depth: float
    processing_length: float
    spindle_speed: float
    feed_rate: float
    comment: str = ""

@dataclass
class MillingOp:
    """
    Stores parameters for the Milling operation.
    
    Attributes:
        removal_depth (float): Total depth to be milled in mm.
        cut_depth (float): Depth of cut per single pass in mm.
        processing_length (float): Length of the milling path in mm.
        feed_rate (float): Feed rate in mm/min (F_min).
        comment (str): Optional comment.
    """
    removal_depth: float
    cut_depth: float
    processing_length: float
    feed_rate: float
    comment: str = ""

@dataclass
class DrillingG1Op:
    """
    Stores parameters for the standard Drilling (G1) operation.
    
    Attributes:
        drilling_depth (float): Total depth of the hole in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
        comment (str): Optional comment.
    """
    drilling_depth: float
    spindle_speed: float
    feed_rate: float
    comment: str = ""

@dataclass
class DrillingQOp:
    """
    Stores parameters for the Peck Drilling (Q) operation.
    
    Attributes:
        drilling_depth (float): Total depth of the hole in mm.
        peck_depth (float): Depth per single peck in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
        comment (str): Optional comment.
    """
    drilling_depth: float
    peck_depth: float
    spindle_speed: float
    feed_rate: float
    comment: str = ""

@dataclass
class WhirlingOp:
    """
    Stores parameters for the Whirling operation.
    
    Attributes:
        processing_length (float): Total length of the thread in mm.
        feed_rate (float): Feed rate in mm/min.
        comment (str): Optional comment.
    """
    processing_length: float
    feed_rate: float
    comment: str = ""

@dataclass
class ThreadingOp:
    """
    Stores parameters for the Threading operation.
    
    Attributes:
        workpiece_diameter (float): Diameter of the thread in mm.
        processing_length (float): Length of the thread in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Thread pitch in mm/rev.
        passes_count (int): Number of threading passes.
        comment (str): Optional comment.
    """
    workpiece_diameter: float
    processing_length: float
    spindle_speed: float
    feed_rate: float # pitch
    passes_count: int
    comment: str = ""

@dataclass
class BroachOp:
    """
    Parameters for broaching/slotting operations.
    
    Attributes:
        removal_depth (float): Total depth to be removed in mm.
        cut_depth (float): Depth per pass in mm.
        processing_length (float): Length of the slot in mm.
        feed_rate (float): Feed rate in mm/min.
        comment (str): Optional comment.
    """
    removal_depth: float
    cut_depth: float
    processing_length: float
    feed_rate: float
    comment: str = ""
