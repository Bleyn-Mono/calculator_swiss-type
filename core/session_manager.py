"""
This module provides a SessionManager class for of calculation results.
Following the SoC principle, this class handles data persistence until report generation.
Supports multi-channel operation (e.g., Main and Back Spindles).
"""

from typing import List, Dict, Any, Optional


class SessionManager:
    """
    Manages the collection of calculation results during a machining session.
    Each instance represents a single channel (e.g., Main Spindle).
    """

    def __init__(self, channel_name: str) -> None:
        """
        Initializes a session for a specific channel.
        
        Args:
            channel_name (str): Name of the channel (e.g., "Main Spindle").
        """
        self.channel_name: str = channel_name
        self._results: List[Dict[str, Any]] = []

    def add_result(self, operation_name: str, processing_time: float, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Adds a single operation result to the session.
        
        Args:
            operation_name (str): The name or type of the operation.
            processing_time (float): Calculated time for the operation in minutes.
            details (Dict[str, Any], optional): Additional parameters for the report.
        """
        result = {
            "channel": self.channel_name,
            "operation": operation_name,
            "time_min": processing_time,
            "details": details or {}
        }
        self._results.append(result)

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Returns all results stored in the current session.
        
        Returns:
            List[Dict[str, Any]]: A list of operation results.
        """
        return self._results

    def remove_result(self, index: int) -> None:
        """
        Removes a result from the session by its index.
        
        Args:
            index (int): The 0-based index of the result to remove.
        """
        if 0 <= index < len(self._results):
            self._results.pop(index)

    def move_result(self, old_index: int, new_index: int) -> None:
        """
        Moves a result from one position to another.
        
        Args:
            old_index (int): Original index of the result.
            new_index (int): New target index.
        """
        if 0 <= old_index < len(self._results) and 0 <= new_index < len(self._results):
            item = self._results.pop(old_index)
            self._results.insert(new_index, item)

    def update_result(self, index: int, operation_name: str, processing_time: float, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Updates an existing operation result in the session.
        
        Args:
            index (int): The 0-based index of the result to update.
            operation_name (str): The name or type of the operation.
            processing_time (float): Calculated time for the operation in minutes.
            details (Dict[str, Any], optional): Additional parameters for the report.
        """
        if 0 <= index < len(self._results):
            self._results[index] = {
                "channel": self.channel_name,
                "operation": operation_name,
                "time_min": processing_time,
                "details": details or {}
            }

    def clear_session(self) -> None:
        """Clears all stored results."""
        self._results = []

    def get_total_time(self) -> float:
        """
        Calculates the total accumulated time for all operations in the session.
        
        Returns:
            float: Total time in minutes.
        """
        return sum(res["time_min"] for res in self._results)
