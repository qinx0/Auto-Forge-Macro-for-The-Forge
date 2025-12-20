import sys
import pyautogui
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QRubberBand
)
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QRect, QPoint

screenSize = pyautogui.size()

class ScreenSelector(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.origin = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.resize(screenSize[0],screenSize[1])

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        self.setCursor(Qt.CursorShape.CrossCursor)
        # self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 10))

    def mousePressEvent(self, event):
        self.origin = event.position().toPoint()
        self.rubber_band.setGeometry(QRect(self.origin, self.origin))
        self.rubber_band.show()

    def mouseMoveEvent(self, event):
        self.rubber_band.setGeometry(
            QRect(self.origin, event.position().toPoint()).normalized()
        )

    def mouseReleaseEvent(self, event):
        rect = self.rubber_band.geometry()
        self.rubber_band.hide()
        self.close()
        self.callback(rect)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auto Forge Macro")
        self.setFixedSize(400, 200)

        # self.label1 = QLabel("*Important: Roblox cant be fullscreen for this to work*")
        # self.label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("No region selected")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.select_button = QPushButton("Select Roblox Bar")
        self.select_button.clicked.connect(self.start_selection)

        layout = QVBoxLayout()
        # layout.addWidget(self.label1)
        layout.addWidget(self.label)
        layout.addWidget(self.select_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.selected_rect = None

    def start_selection(self):
        self.hide()  # Hide main window during selection
        self.selector = ScreenSelector(self.on_region_selected)
        self.selector.show()

    def on_region_selected(self, rect: QRect):
        self.show()
        self.selected_rect = rect

        self.label.setText(
            f"Selected: x={rect.x()}, y={rect.y()}, "
            f"w={rect.width()}, h={rect.height()}"
        )

        print("Minigame bar region:", rect)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
