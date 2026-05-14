"""
This module contains the BaseCalculator class which implements fundamental 
machining formulas used across various types of operations.
"""

import math


class BaseCalculator:
    """
    Base class for machining calculations.
    Provides methods for calculating processing time for turning and milling operations,
    incorporating both working time and rapid traverse time.
    """

    @staticmethod
    def calculate_turning_time(
        processing_length: float,
        spindle_speed: float,
        feed_rate: float,
        rapid_traverse: float
    ) -> float:
        """
        Calculates the total time for a turning or drilling operation.
        
        Formula:
        T_total = T_work + T_rapid
        T_work = L / (S * F)
        T_rapid = (1.3 * L) / Rapid_Traverse
        
        Args:
            processing_length (float): Length of the machining path in mm.
            spindle_speed (float): Spindle rotation speed in RPM.
            feed_rate (float): Feed rate in mm/rev.
            rapid_traverse (float): Rapid traverse speed in mm/min from machine config.
            
        Returns:
            float: Total operation time in minutes.
        """
        if spindle_speed <= 0 or feed_rate <= 0 or rapid_traverse <= 0:
            return 0.0

        t_work = processing_length / (spindle_speed * feed_rate)
        t_rapid = (1.3 * processing_length) / rapid_traverse
        
        return t_work + t_rapid

    @staticmethod
    def calculate_milling_time(
        processing_length: float,
        feed_min: float,
        rapid_traverse: float
    ) -> float:
        """
        Calculates the total time for a milling operation.
        
        Formula:
        T_total = T_work + T_rapid
        T_work = L / F_min
        T_rapid = (1.2 * L) / Rapid_Traverse
        
        Args:
            processing_length (float): Length of the machining path in mm.
            feed_min (float): Feed rate in mm/min.
            rapid_traverse (float): Rapid traverse speed in mm/min from machine config.
            
        Returns:
            float: Total operation time in minutes.
        """
        if feed_min <= 0 or rapid_traverse <= 0:
            return 0.0

        t_work = processing_length / feed_min
        t_rapid = (1.2 * processing_length) / rapid_traverse
        
        return t_work + t_rapid
