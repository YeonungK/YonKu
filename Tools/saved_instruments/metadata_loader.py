import importlib
import json
from pathlib import Path


METADATA_FIELDS = ("data_label", "data_unit", "value_format")


def _validate_metadata(model_name, metadata):
    data_type = metadata.get("data_type", {})
    if not isinstance(data_type, dict):
        raise ValueError(f"{model_name}: data_type must be an object")

    for data_type_id, channels in data_type.items():
        if not isinstance(data_type_id, str) or not isinstance(channels, list):
            raise ValueError(
                f"{model_name}: each data_type entry must map a string ID to a channel list"
            )
        if not all(isinstance(channel, str) for channel in channels):
            raise ValueError(f"{model_name}: channels for {data_type_id} must be strings")

    for field in METADATA_FIELDS:
        values = metadata.get(field, {})
        if not isinstance(values, dict):
            raise ValueError(f"{model_name}: {field} must be an object")
        for data_type_id, channel_values in values.items():
            if not isinstance(channel_values, dict):
                raise ValueError(
                    f"{model_name}: {field}.{data_type_id} must be keyed by channel"
                )

    data_function_types = set()
    for command_name, info in metadata.get("methods", {}).items():
        linked_data = info.get("command_linked_data", {})
        if not linked_data.get("data_function", False):
            continue
        data_type_id = linked_data.get("data_type")
        if data_type_id not in data_type:
            raise ValueError(
                f"{model_name}: {command_name} links to unknown data type {data_type_id!r}"
            )
        if data_type_id in data_function_types:
            raise ValueError(
                f"{model_name}: more than one data function is linked to {data_type_id!r}"
            )
        data_function_types.add(data_type_id)


def load_model_metadata(model_name, model_file):
    model_dir = Path(model_file).resolve().parent
    metadata_path = model_dir / "metadata.json"

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    _validate_metadata(model_name, metadata)

    functions = {}
    read_functions = {}
    write_functions = {}
    data_functions = {}
    package_root = f"Tools.saved_instruments.{model_name}"

    for command_name, info in metadata.get("methods", {}).items():
        module_name = info.get("module", command_name)
        function_name = info.get("function", "run")
        module_path = f"{package_root}.methods.{module_name}"

        try:
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)
        except Exception as error:
            print(f"Failed to load {model_name} command {command_name}: {error}")
            continue

        functions[command_name] = function
        command_type = info.get("command_type", "").upper()

        if command_type == "READ":
            read_functions[command_name] = function
        elif command_type == "WRITE":
            write_functions[command_name] = function

        linked_data = info.get("command_linked_data", {})
        if linked_data.get("data_function") is True:
            data_type_id = linked_data.get("data_type")
            if data_type_id:
                data_functions[data_type_id] = function

    return {
        "metadata": metadata,
        "data_type": metadata.get("data_type", {}),
        "data_label": metadata.get("data_label", {}),
        "data_unit": metadata.get("data_unit", {}),
        "value_format": metadata.get("value_format", {}),
        "initial_state": metadata.get("initial_state", {}),
        "functions": functions,
        "read_functions": read_functions,
        "write_functions": write_functions,
        "data_functions": data_functions,
    }
