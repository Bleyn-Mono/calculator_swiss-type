
from core.operations import FacingOp, DrillingG1Op
from core.specific_calc import FacingCalculator, DrillingG1Calculator
from utils.config_loader import MachineConfig

machine_config: MachineConfig = {
    "rapid_traverse_mm_min": 15000,
    "tool_change_time_s": 1.2,
    "cutoff_time_s": 4.5,
    "re_grip_time_s": 3.0,
    "ejection_time_s": 1.5
}

def test_facing():
    data = {
        "workpiece_diameter": 20.0,
        "spindle_speed": 1000.0,
        "feed_rate": 0.1
    }
    op = FacingOp(**data)
    time = FacingCalculator.calculate(op, machine_config)
    print(f"Facing time: {time}")
    assert time > 0

def test_drilling():
    data = {
        "drilling_depth": 30.0,
        "spindle_speed": 1500.0,
        "feed_rate": 0.05
    }
    op = DrillingG1Op(**data)
    time = DrillingG1Calculator.calculate(op, machine_config)
    print(f"Drilling time: {time}")
    assert time > 0

if __name__ == "__main__":
    try:
        test_facing()
        test_drilling()
        print("Tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
