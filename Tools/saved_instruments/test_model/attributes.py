import json
import importlib
from pathlib import Path
from project_paths import PROJECT_ROOT

MODEL_NAME = "test_model"

MODEL_DIR = Path(__file__).resolve().parent
METADATA_PATH = MODEL_DIR / "metadata.json"

PACKAGE_ROOT = f"Tools.saved_instruments.{MODEL_NAME}"


data_type = {}
data_label = {}
data_unit = {}
initial_state = {}

functions = {}
read_functions = {}
data_functions = {}
write_functions = {}



def load_metadata():
    global data_type, data_label, data_unit, initial_state

    if not METADATA_PATH.exists():
        return

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
        module_path = f"{PACKAGE_ROOT}.methods.{command_name}"
        module = importlib.import_module(module_path)

        if not hasattr(module, "run"):
            continue

        functions[command_name] = module.run

        method_type = info.get("command_type")

        if method_type == "read":
            read_functions[command_name] = module.run
        elif method_type == "write":
            write_functions[command_name] = module.run

        method_linked_data = info.get("command_linked_data")
        
        if method_linked_data["data_function"]:
            temp_data_type = data_type.get(method_linked_data["data_type"])
            data_functions[temp_data_type] = module.run


metadata = load_metadata() or {}
load_methods(metadata)
