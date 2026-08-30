"""Helpers shared by the per-interface device detail widgets."""

from pathlib import Path
import json
import shutil
import stat

from project_paths import (
    INSTRUMENT_CONTROL_UIS_DIR,
    INSTRUMENT_WIDGETS_DIR,
    SAVED_DEVICES_DIR,
    SAVED_INSTRUMENTS_DIR,
)


def _remove_readonly(func, path, _):
    """Make a generated file writable before retrying its removal on Windows."""
    Path(path).chmod(stat.S_IWRITE)
    func(path)


def _other_device_uses_model(model: str, removed_config: Path) -> bool:
    """Return whether a saved device other than ``removed_config`` uses ``model``."""
    for config_path in SAVED_DEVICES_DIR.glob("*.json"):
        if config_path == removed_config:
            continue
        try:
            with config_path.open(encoding="utf-8") as config_file:
                if json.load(config_file).get("model") == model:
                    return True
        except (OSError, json.JSONDecodeError):
            # A malformed unrelated configuration should not prevent removal.
            continue
    return False


def remove_device(model: str, config_path: Path) -> None:
    """Remove a device configuration and, when unused, its generated resources."""
    config_path = Path(config_path)
    if config_path.is_file():
        config_path.unlink()
    else:
        print(f"Error: saved-device config not found: {config_path}")

    # A model may be shared by multiple configured devices.  In that case, its
    # generated package/widget must remain available for the other devices.
    if _other_device_uses_model(model, config_path):
        return

    files_to_remove = (
        SAVED_INSTRUMENTS_DIR / f"{model}.py",  # legacy layout
        INSTRUMENT_WIDGETS_DIR / f"{model}_widget.py",
        INSTRUMENT_CONTROL_UIS_DIR / f"{model}_ui.ui",
        INSTRUMENT_CONTROL_UIS_DIR / f"{model}_ui.json",
    )
    directories_to_remove = (
        SAVED_INSTRUMENTS_DIR / "Members" / model,  # legacy layout
        SAVED_INSTRUMENTS_DIR / model,                # current package layout
    )

    for path in files_to_remove:
        if path.is_file():
            path.unlink()
    for path in directories_to_remove:
        if path.is_dir():
            shutil.rmtree(path, onerror=_remove_readonly)
