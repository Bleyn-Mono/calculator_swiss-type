"""
This module contains data classes for storing parameters of various machining operations.
Following the OOP first principle, each operation is represented by a dedicated class.
"""

from dataclasses import dataclass


@dataclass
class FacingOp:
    """
    Stores parameters for the Facing operation.
    
    Attributes:
        workpiece_diameter (float): Diameter of the workpiece in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
    """
    workpiece_diameter: float
    spindle_speed: float
    feed_rate: float


@dataclass
class TurningOp:
    """
    Stores parameters for the Turning operation.
    
    Attributes:
        removal_depth (float): Total depth of material to be removed in mm.
        cut_depth (float): Depth of a single cut in mm.
        processing_length (float): Length of the machining path in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
    """
    removal_depth: float
    cut_depth: float
    processing_length: float
    spindle_speed: float
    feed_rate: float


@dataclass
class MillingOp:
    """
    Stores parameters for the Milling operation.
    
    Attributes:
        removal_depth (float): Total depth of material to be removed in mm.
        cut_depth (float): Depth of a single cut in mm.
        processing_length (float): Length of the machining path in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Feed rate in mm/min.
    """
    removal_depth: float
    cut_depth: float
    processing_length: float
    spindle_speed: float
    feed_rate: float


@dataclass
class DrillingG1Op:
    """
    Stores parameters for the Drilling (G1) operation (standard drilling).
    
    Attributes:
        drilling_depth (float): Total depth of the hole in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
    """
    drilling_depth: float
    spindle_speed: float
    feed_rate: float


@dataclass
class DrillingQOp:
    """
    Stores parameters for the Drilling (Q) operation (peck drilling).
    
    Attributes:
        drilling_depth (float): Total depth of the hole in mm.
        peck_depth (float): Depth of each peck (Q value) in mm.
        spindle_speed (float): Rotation speed in RPM.
        feed_rate (float): Feed rate in mm/rev.
    """
    drilling_depth: float
    peck_depth: float
    spindle_speed: float
    feed_rate: float


@dataclass
class WhirlingOp:
    """
    Stores parameters for the Whirling operation.
    
    Attributes:
        processing_length (float): Length of the machining path in mm.
        feed_rate (float): Feed rate in mm/rev or mm/min.
    """
    processing_length: float
    feed_rate: float


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
    """
    workpiece_diameter: float
    processing_length: float
    spindle_speed: float
    feed_rate: float
    passes_count: int
