from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class connect_warning_ui(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Device Required")
        self.setFixedSize(350, 120)  # small window size

        layout = QVBoxLayout()

        label = QLabel("The device has to be connected to proceed.")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)

        layout.addWidget(label)
        self.setLayout(layout)

        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
