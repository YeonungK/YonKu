from pathlib import Path
import sys

# Ensure YonKu root is importable
PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Main folders
GUI_DIR = PROJECT_ROOT / "GUI"
TOOLS_DIR = PROJECT_ROOT / "Tools"
DATA_DIR = PROJECT_ROOT / "Data"

# UI files
UI_FILES_DIR = GUI_DIR / "ui_files"
GRAPHENE_UI_PATH = UI_FILES_DIR / "graphene.ui"

# Data
EXPERIMENT_DATA_DIR = DATA_DIR / "experiment_data"
EXPERIMENT_PARAMETERS_DIR = DATA_DIR / "experiment_parameters"
SAVED_DEVICES_DIR = DATA_DIR / "saved_devices"

# Generated/custom instrument resources
SAVED_INSTRUMENTS_DIR = TOOLS_DIR / "saved_instruments"
INSTRUMENT_WIDGETS_DIR = GUI_DIR / "instrument_control_widgets"
INSTRUMENT_CONTROL_UIS_DIR = UI_FILES_DIR / "instrument_control_uis"


def ensure_project_dirs():
    for path in [
        DATA_DIR,
        EXPERIMENT_DATA_DIR,
        EXPERIMENT_PARAMETERS_DIR,
        SAVED_DEVICES_DIR,
        SAVED_INSTRUMENTS_DIR,
        INSTRUMENT_WIDGETS_DIR,
        INSTRUMENT_CONTROL_UIS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)