import json
from pathlib import Path
from typing import Dict, Any
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class MachineConfig(TypedDict):
    """
    Typed definition of a single machine's configuration.
    Ensures type safety when accessing configuration parameters.
    """
    description: str
    rapid_traverse_mm_min: int
    tool_change_time_s: float
    cutoff_time_s: float
    re_grip_time_s: float
    ejection_time_s: float


class ConfigLoader:
    """
    Utility class for loading and validating machine configurations from JSON.
    Following the Separation of Concerns principle.
    """

    @staticmethod
    def load_config(file_path: str = "machines_config.json") -> Dict[str, MachineConfig]:
        """
        Loads the machine configuration from a JSON file.

        Args:
            file_path (str): Path to the configuration file.

        Returns:
            Dict[str, MachineConfig]: A dictionary where keys are machine names 
                                      and values are MachineConfig typed dicts.

        Raises:
            FileNotFoundError: If the config file does not exist.
            json.JSONDecodeError: If the file is not a valid JSON.
            KeyError: If mandatory fields are missing in the configuration (optional validation).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with path.open('r', encoding='utf-8') as f:
            data: Dict[str, Any] = json.load(f)

        # In a real-world scenario, we might want to validate that each entry
        # matches the MachineConfig structure. For now, we cast it for type hinting.
        return data  # type: ignore
