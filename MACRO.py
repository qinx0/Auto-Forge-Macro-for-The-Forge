import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auto Forge Macro")
        self.setMinimumSize(400, 200)

        # Central widget (required for QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Widgets
        self.label = QLabel("Ready")
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Click me")
        self.button.clicked.connect(self.on_button_clicked)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        central_widget.setLayout(layout)

    def on_button_clicked(self):
        self.label.setText("Button clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
