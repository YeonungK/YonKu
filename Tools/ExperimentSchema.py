def build_experiment_schema(instruments, experiment_setting_wid=None):
    if experiment_setting_wid is not None:
        experiment_setting_wid.save_all_values()
        exp_params = experiment_setting_wid.experiment_parameters
    else:
        exp_params = {}

    data_schema = {
        "time_time": {
            "label": exp_params.get("time_name", {}).get("time", "time"),
        }
    }

    available_data_types = ["time"]

    devices = []

    for device_key, inst in instruments.items():
        devices.append({
            "device_id": device_key,
            "name": getattr(inst, "name", device_key),
            "model": getattr(inst, "model", "unknown"),
            "data_types": list(getattr(inst, "data_type", {}).keys())
        })

        for data_type, channels in getattr(inst, "data_type", {}).items():
            if data_type not in available_data_types:
                available_data_types.append(data_type)

            for channel in channels:
                schema_key = f"{data_type}_{channel}"

                label = exp_params.get(f"{data_type}_name", {}).get(channel)
                unit = exp_params.get(f"{data_type}_unit", {}).get(channel)

                if label is None:
                    label = getattr(inst, "data_label", {}).get(data_type, {}).get(channel, channel)

                if unit is None:
                    unit = getattr(inst, "data_unit", {}).get(data_type, {}).get(channel, "-")

                data_schema[schema_key] = {
                    "label": label,
                    "unit": unit
                }

    return {
        "devices": devices,
        "available_data_types": available_data_types,
        "data_schema": data_schema
    }