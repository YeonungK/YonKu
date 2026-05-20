
import json
import importlib
from pathlib import Path
from project_paths import PROJECT_ROOT

MODEL_NAME = "test_serial_two_model"

MODEL_DIR = Path(__file__).resolve().parent
METADATA_PATH = MODEL_DIR / "metadata.json"

PACKAGE_ROOT = f"Tools.saved_instruments.{MODEL_NAME}"

data_type = {}
data_label = {}
data_unit = {}
initial_state = {}

functions = {}
read_functions = {}
write_functions = {}
data_functions = {}


def load_metadata():
    global data_type, data_label, data_unit, initial_state

    if not METADATA_PATH.exists():
        return {}

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    data_type = metadata.get("data_type", {})
    data_label = metadata.get("data_label", {})
    data_unit = metadata.get("data_unit", {})
    initial_state = metadata.get("initial_state", {})

    return metadata


def load_methods(metadata):
    functions.clear()
    read_functions.clear()
    write_functions.clear()
    data_functions.clear()

    for command_name, info in metadata.get("methods", {}).items():
        module_name = info.get("module", command_name)
        function_name = info.get("function", "run")

        module_path = f"{PACKAGE_ROOT}.methods.{module_name}"

        try:
            module = importlib.import_module(module_path)
        except Exception as e:
            print(f"Failed to import method module {module_path}: {e}")
            continue

        if not hasattr(module, function_name):
            print(f"Method module {module_path} has no function {function_name}")
            continue

        func = getattr(module, function_name)
        functions[command_name] = func

        command_type = info.get("command_type", "").upper()

        if command_type == "READ":
            read_functions[command_name] = func
        elif command_type == "WRITE":
            write_functions[command_name] = func

        linked_data = info.get("command_linked_data", {})
        if linked_data.get("data_function") is True:
            linked_data_type = linked_data.get("data_type")
            if linked_data_type:
                data_functions[linked_data_type] = func


metadata = load_metadata()
load_methods(metadata)