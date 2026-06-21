from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QGridLayout,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
from PyQt5 import uic

from project_paths import GUI_DIR


class ExperimentSettingUi(QWidget):
    def __init__(self, instruments=None):
        super().__init__()

        # Optional: load base UI if it works.
        # If your .ui keeps causing Qt enum errors, comment this out.
        # uic.loadUi(f"{GUI_DIR}/ui_files/experiment_setting.ui", self)

        self.instruments = instruments or {}
        self.setting_widgets = {}

        self.experiment_parameters = {
            "data_schema": {}
        }

        self.build_ui()
        self.build_dynamic_rows()

    def build_ui(self):
        self.mainLayout = QVBoxLayout(self)

        title = QLabel("Experiment Settings")
        self.mainLayout.addWidget(title)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.scrollWidget = QWidget()
        self.dynamicGridLayout = QGridLayout(self.scrollWidget)

        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)

        self.saveButton = QPushButton("Save")
        self.cancelButton = QPushButton("Cancel")

        self.saveButton.clicked.connect(self.save_button)
        self.cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)

        self.mainLayout.addLayout(buttonLayout)

    def build_dynamic_rows(self):
        headers = ["Data Type", "Channel", "Label", "Unit"]

        for col, text in enumerate(headers):
            self.dynamicGridLayout.addWidget(QLabel(text), 0, col)

        row = 1

        self.add_schema_row(
            row=row,
            data_type="time",
            channel="time",
            default_label="time",
            default_unit="s"
        )
        row += 1

        for device_key, inst in self.instruments.items():
            for data_type, channels in getattr(inst, "data_type", {}).items():
                for channel in channels:
                    default_label = getattr(inst, "data_label", {}).get(
                        data_type, {}
                    ).get(channel, channel)

                    default_unit = getattr(inst, "data_unit", {}).get(
                        data_type, {}
                    ).get(channel, "")

                    self.add_schema_row(
                        row=row,
                        data_type=data_type,
                        channel=channel,
                        default_label=default_label,
                        default_unit=default_unit
                    )

                    row += 1

    def add_schema_row(self, row, data_type, channel, default_label, default_unit):
        schema_key = f"{data_type}_{channel}"

        data_type_label = QLabel(data_type)
        channel_label = QLabel(channel)

        label_line_edit = QLineEdit()
        label_line_edit.setText(default_label)

        unit_line_edit = QLineEdit()
        unit_line_edit.setText(default_unit)

        self.dynamicGridLayout.addWidget(data_type_label, row, 0)
        self.dynamicGridLayout.addWidget(channel_label, row, 1)
        self.dynamicGridLayout.addWidget(label_line_edit, row, 2)
        self.dynamicGridLayout.addWidget(unit_line_edit, row, 3)

        self.setting_widgets[schema_key] = {
            "data_type": data_type,
            "channel": channel,
            "label_widget": label_line_edit,
            "unit_widget": unit_line_edit
        }

    def save_button(self):
        self.save_all_values()

    def save_all_values(self):
        data_schema = {}

        for schema_key, item in self.setting_widgets.items():
            data_schema[schema_key] = {
                "data_type": item["data_type"],
                "channel": item["channel"],
                "label": item["label_widget"].text(),
                "unit": item["unit_widget"].text()
            }

        self.experiment_parameters = {
            "data_schema": data_schema
        }

