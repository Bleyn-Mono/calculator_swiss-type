"""
This module implements the 'glue logic' for specific machining operations.
Each class handles the transformation of operation-specific data and machine
configuration into calls for the BaseCalculator formulas.
"""

import math
from typing import Any
from .operations import (
    FacingOp, TurningOp, MillingOp, DrillingG1Op, 
    DrillingQOp, WhirlingOp, ThreadingOp, BroachOp
)
from .base_calculator import BaseCalculator
from utils.config_loader import MachineConfig


class FacingCalculator:
    """Calculates time for facing operations."""
    
    @staticmethod
    def calculate(op: FacingOp, machine: MachineConfig) -> float:
        """
        Path length is assumed to be the radius of the workpiece (D/2).
        Uses turning time formula.
        """
        path_length = op.workpiece_diameter / 2
        return BaseCalculator.calculate_turning_time(
            path_length,
            op.spindle_speed,
            op.feed_rate,
            machine['rapid_traverse_mm_min']
        )


class TurningCalculator:
    """Calculates time for turning operations with multi-pass support."""
    
    @staticmethod
    def calculate(op: TurningOp, machine: MachineConfig) -> float:
        """
        Calculates number of passes based on removal and cut depth.
        Multiplies processing length by the number of passes.
        """
        if op.cut_depth <= 0:
            return 0.0
            
        passes = math.ceil(op.removal_depth / op.cut_depth)
        total_path = op.processing_length * passes
        
        return BaseCalculator.calculate_turning_time(
            total_path,
            op.spindle_speed,
            op.feed_rate,
            machine['rapid_traverse_mm_min']
        )


class MillingCalculator:
    """Calculates time for milling operations with multi-pass support."""
    
    @staticmethod
    def calculate(op: MillingOp, machine: MachineConfig) -> float:
        """
        Calculates number of passes and uses milling time formula (minutely feed).
        """
        if op.cut_depth <= 0:
            return 0.0
            
        passes = math.ceil(op.removal_depth / op.cut_depth)
        total_path = op.processing_length * passes
        
        return BaseCalculator.calculate_milling_time(
            total_path,
            op.feed_rate, # In milling, feed_rate is mm/min (F_min)
            machine['rapid_traverse_mm_min']
        )


class DrillingG1Calculator:
    """Calculates time for standard G1 drilling."""
    
    @staticmethod
    def calculate(op: DrillingG1Op, machine: MachineConfig) -> float:
        """Uses turning time formula for standard drilling path."""
        return BaseCalculator.calculate_turning_time(
            op.drilling_depth,
            op.spindle_speed,
            op.feed_rate,
            machine['rapid_traverse_mm_min']
        )


class DrillingQCalculator:
    """Calculates time for peck drilling (Q)."""
    
    @staticmethod
    def calculate(op: DrillingQOp, machine: MachineConfig) -> float:
        """
        Calculates time for peck drilling by accounting for multiple 
        retracts and re-entries.
        """
        if op.peck_depth <= 0:
            return 0.0
            
        n_pecks = math.ceil(op.drilling_depth / op.peck_depth)
        
        # Working time is the same as standard drilling
        t_work = 0.0
        if op.spindle_speed > 0 and op.feed_rate > 0:
            t_work = op.drilling_depth / (op.spindle_speed * op.feed_rate)
            
        # Rapid traverse time is significantly higher due to retracts.
        # Approximation: Each peck i travels i*Q to retract and back.
        # Sum(2 * i * Q) for i=1 to n_pecks = 2 * Q * (n_pecks * (n_pecks + 1) / 2)
        # = Q * n_pecks * (n_pecks + 1)
        rapid_path = op.peck_depth * n_pecks * (n_pecks + 1)
        t_rapid = rapid_path / machine['rapid_traverse_mm_min']
        
        return t_work + t_rapid


class WhirlingCalculator:
    """Calculates time for whirling operations."""
    
    @staticmethod
    def calculate(op: WhirlingOp, machine: MachineConfig) -> float:
        """
        Calculates time for whirling. 
        Assumes milling-style minutely feed calculation.
        """
        return BaseCalculator.calculate_milling_time(
            op.processing_length,
            op.feed_rate,
            machine['rapid_traverse_mm_min']
        )


class ThreadingCalculator:
    """Calculates time for threading operations."""
    
    @staticmethod
    def calculate(op: ThreadingOp, machine: MachineConfig) -> float:
        """
        Total path is length * passes.
        Uses turning time formula with spindle speed and pitch (feed_rate).
        """
        total_path = op.processing_length * op.passes_count
        
        return BaseCalculator.calculate_turning_time(
            total_path,
            op.spindle_speed,
            op.feed_rate, # pitch
            machine['rapid_traverse_mm_min']
        )


class BroachCalculator:
    """Calculates time for broaching/slotting operations with multi-pass support."""
    
    @staticmethod
    def calculate(op: BroachOp, machine: MachineConfig) -> float:
        """
        Calculates number of passes and uses milling time formula (minutely feed).
        Broaching is a linear operation, using mm/min feed.
        """
        if op.cut_depth <= 0:
            return 0.0
            
        passes = math.ceil(op.removal_depth / op.cut_depth)
        total_path = op.processing_length * passes
        
        return BaseCalculator.calculate_milling_time(
            total_path,
            op.feed_rate,
            machine['rapid_traverse_mm_min']
        )
