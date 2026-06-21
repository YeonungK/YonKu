import ast
import json
from pathlib import Path


def load_experiment_parameters(param_path):
    """
    Supports both:
    - new .json experiment parameter files
    - old .txt experiment parameter files
    """
    param_path = Path(param_path)
    base = param_path.with_suffix("")  # remove extension

    for ext in [".json", ".txt"]:
        file_path = base.with_suffix(ext)
        if file_path.exists():
            param_path = file_path
            break
    else:
        return _default_legacy_experiment_parameters()

    if param_path.suffix.lower() == ".json":
        with open(param_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if param_path.suffix.lower() == ".txt":
        return parse_old_txt_experiment_parameters(param_path)

    raise ValueError(f"Unsupported parameter file type: {param_path.suffix}")


def parse_old_txt_experiment_parameters(param_path):
    """
    Converts old text parameter files into a normalized dictionary.
    """
    params = {}
    connected_models = []
    available_data_types = ["time"]

    with open(param_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                try:
                    connected_models = ast.literal_eval(line)
                except Exception:
                    connected_models = ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2']
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                params[key.strip()] = value.strip()

    for model in connected_models:
        match model:
            case 'Lakeshore_336':
                available_data_types.extend(['temperature', 'resistance'])
            case 'Oxford_MercuryiPS':
                available_data_types.extend(['field', 'current'])
            case 'SRS_830':
                available_data_types.extend(['lockIn'])
            case 'SRS_830_2':
                available_data_types.extend(['lockIn2'])

    return {
        "format": "legacy_txt",
        "metadata": {
            "start_datetime": params.get("startDatetime", ""),
            "name": params.get("name", ""),
            "measurement_period_ms": params.get("measurementPeriod", "")
        },
        "data_schema": {
            "temperature_ch_A": {
                "label": params.get("temperature_ch_A_label", "Ch_A"),
                "unit": params.get("temperature_ch_A_unit", "K")
            },
            "temperature_ch_B": {
                "label": params.get("temperature_ch_B_label", "Ch_B"),
                "unit": params.get("temperature_ch_B_unit", "K")
            },
            "temperature_ch_C": {
                "label": params.get("temperature_ch_C_label", "Ch_C"),
                "unit": params.get("temperature_ch_C_unit", "K")
            },
            "temperature_ch_D": {
                "label": params.get("temperature_ch_D_label", "Ch_D"),
                "unit": params.get("temperature_ch_D_unit", "K")
            },
            "resistance_ch_A": {
                "label": params.get("resistance_ch_A_label", "Ch_A"),
                "unit": params.get("resistance_ch_A_unit", "Ohms")
            },
            "resistance_ch_B": {
                "label": params.get("resistance_ch_B_label", "Ch_B"),
                "unit": params.get("resistance_ch_B_unit", "Ohms")
            },
            "resistance_ch_C": {
                "label": params.get("resistance_ch_C_label", "Ch_C"),
                "unit": params.get("resistance_ch_C_unit", "Ohms")
            },
            "resistance_ch_D": {
                "label": params.get("resistance_ch_D_label", "Ch_D"),
                "unit": params.get("resistance_ch_D_unit", "Ohms")
            },
            "lockIn_x": {
                "label": params.get("lockIn_x_label", "X"),
                "unit": params.get("lockIn_x_unit", "manual")
            },
            "lockIn_y": {
                "label": params.get("lockIn_y_label", "Y"),
                "unit": params.get("lockIn_y_unit", "manual")
            },
            "lockIn_r": {
                "label": params.get("lockIn_r_label", "R"),
                "unit": params.get("lockIn_r_unit", "manual")
            },
            "lockIn_theta": {
                "label": params.get("lockIn_theta_label", "Theta"),
                "unit": params.get("lockIn_theta_unit", "degrees")
            },
            "lockIn2_x": {
                "label": params.get("lockIn2_x_label", "X"),
                "unit": params.get("lockIn2_x_unit", "manual")
            },
            "lockIn2_y": {
                "label": params.get("lockIn2_y_label", "Y"),
                "unit": params.get("lockIn2_y_unit", "manual")
            },
            "lockIn2_r": {
                "label": params.get("lockIn2_r_label", "R"),
                "unit": params.get("lockIn2_r_unit", "manual")
            },
            "lockIn2_theta": {
                "label": params.get("lockIn2_theta_label", "Theta"),
                "unit": params.get("lockIn2_theta_unit", "degrees")
            },
            "field": {
                "label": params.get("field_label", "field"),
                "unit": params.get("field_unit", "T")
            },
            "current": {
                "label": params.get("current_label", "current"),
                "unit": params.get("current_unit", "A")
            },
            "time": {
                "label": params.get("time_label", "time"),
                "unit": params.get("time_unit", "s")
            }
        },
        "connected_models": connected_models,
        "available_data_types": available_data_types
    }


def _default_legacy_experiment_parameters():
    return {
        "format": "legacy_txt",
        "metadata": {
            "start_datetime": "",
            "name": "",
            "measurement_period_ms": ""
        },
        "data_schema": {
            "temperature_ch_A": {
                "label": "Ch_A",
                "unit": "K"
            },
            "temperature_ch_B": {
                "label": "Ch_B",
                "unit": "K"
            },
            "temperature_ch_C": {
                "label": "Ch_C",
                "unit": "K"
            },
            "temperature_ch_D": {
                "label": "Ch_D",
                "unit": "K"
            },
            "resistance_ch_A": {
                "label": "Ch_A",
                "unit": "Ohms"
            },
            "resistance_ch_B": {
                "label": "Ch_B",
                "unit": "Ohms"
            },
            "resistance_ch_C": {
                "label": "Ch_C",
                "unit": "Ohms"
            },
            "resistance_ch_D": {
                "label": "Ch_D",
                "unit": "Ohms"
            },
            "lockIn_x": {
                "label": "X",
                "unit": "manual"
            },
            "lockIn_y": {
                "label": "Y",
                "unit": "manual"
            },
            "lockIn_r": {
                "label": "R",
                "unit": "manual"
            },
            "lockIn_theta": {
                "label": "Theta",
                "unit": "degrees"
            },
            "lockIn2_x": {
                "label": "X",
                "unit": "manual"
            },
            "lockIn2_y": {
                "label": "Y",
                "unit": "manual"
            },
            "lockIn2_r": {
                "label": "R",
                "unit": "manual"
            },
            "lockIn2_theta": {
                "label": "Theta",
                "unit": "degrees"
            },
            "field": {
                "label": "field",
                "unit": "T"
            },
            "current": {
                "label": "current",
                "unit": "A"
            },
            "time": {
                "label": "time",
                "unit": "s"
            }
        },
        "connected_models": ['Lakeshore_336', 'Oxford_MercuryiPS', 'SRS_830', 'SRS_830_2'],
        "available_data_types": ['time', 'temperature', 'resistance', 'lockIn', 'lockIn2', 'field', 'current']
    }
