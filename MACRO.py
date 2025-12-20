import sys
import pyautogui
import time

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout
)
from PyQt6.QtCore import Qt

from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly
)

# ----------------------------
# Relative region definitions
# ----------------------------

MINIGAME_BAR_REL = {
    "x": 0.888,
    "y": 0.19,
    "w": 0.05,
    "h": 0.65,
}

PUMP_REL = {
    "x": 0.15,
    "y": 0.42,
    "w": 0.10,
    "h": 0.30,
}


# ----------------------------
# Debug
# ----------------------------

# def test_pump(self):
#     win = get_roblox_window()
#     if not win:
#         self.label.setText("❌ Roblox not found")
#         return

#     self.label.setText("🔍 Debugging pump path...")
#     debug_pump_path(win, PUMP_REL)

def debug_pump_path(win, rel):
    x, y_top, y_bottom = pump_points(win, rel)
    pyautogui.moveTo(x, y_top)
    time.sleep(1)
    pyautogui.moveTo(x, y_bottom)

# ----------------------------
# macOS: Find Roblox window
# ----------------------------

def get_roblox_window():
    windows = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly, 0
    )

    for w in windows:
        owner = w.get("kCGWindowOwnerName", "")
        if owner == "Roblox":
            b = w["kCGWindowBounds"]
            return (
                int(b["X"]),
                int(b["Y"]),
                int(b["Width"]),
                int(b["Height"])
            )
    return None


def resolve_region(win, rel):
    wx, wy, ww, wh = win
    return (
        int(wx + rel["x"] * ww),
        int(wy + rel["y"] * wh),
        int(rel["w"] * ww),
        int(rel["h"] * wh),
    )

def pump_points(win, rel):
    wx, wy, ww, wh = win

    # Slightly left of center of pump handle
    x = int(wx + (rel["x"] + rel["w"] * 0.45) * ww)

    y_top = int(wy + rel["y"] * wh)
    y_bottom = int(wy + (rel["y"] + rel["h"]) * wh)

    return x, y_top, y_bottom

def perform_pump(win, rel):
    x, y_top, y_bottom = pump_points(win, rel)

    # Move to TOP first (important)
    pyautogui.moveTo(x, y_top, duration=0.2)
    time.sleep(0.05)

    pyautogui.mouseDown()

    # for _ in range(cycles):
    #     pyautogui.mouseDown()
    #     pyautogui.moveTo(x, y_bottom, duration=0.05)
    #     pyautogui.moveTo(x, y_top, duration=0.05)
    while True:
        try:
            finishedPumpLocation = pyautogui.locateOnScreen("pumpFinished.png", confidence=0.5)
            print(f'found finished pump bar at {finishedPumpLocation}')
            pyautogui.mouseDown()
            pyautogui.moveTo(x, y_bottom, duration=0.05)
            pyautogui.moveTo(x, y_top, duration=0.05)
            break
        except Exception as e:
            print("Not found finished pump bar")
            pyautogui.mouseDown()
            pyautogui.moveTo(x, y_bottom, duration=0.05)
            pyautogui.moveTo(x, y_top, duration=0.05)

    pyautogui.mouseUp()


# ----------------------------
# Main PyQt6 Window
# ----------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auto Forge Macro")
        self.setFixedSize(420, 240)

        self.label = QLabel("Ready")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.detect_button = QPushButton("Test Auto-Detect Minigame Bar")
        self.detect_button.clicked.connect(self.test_auto_detect)

        self.pump_button = QPushButton("Test Pump Minigame")
        self.pump_button.clicked.connect(self.test_pump)

        layout = QVBoxLayout()
        layout.addWidget(self.pump_button)
        layout.addWidget(self.label)
        layout.addWidget(self.detect_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def test_auto_detect(self):
        win = get_roblox_window()

        if not win:
            self.label.setText("❌ Roblox window not found")
            return

        region = resolve_region(win, MINIGAME_BAR_REL)
        x, y, w, h = region

        self.label.setText(f"Bar: x={x}, y={y}, w={w}, h={h}")

        # Visual confirmation
        img = pyautogui.screenshot(region=region)
        img.show()

    # def test_pump(self):
    #     win = get_roblox_window()
    #     if not win:
    #         self.label.setText("❌ Roblox not found")
    #         return

    #     self.label.setText("🔍 Debugging pump path...")
    #     debug_pump_path(win, PUMP_REL)
    def test_pump(self):
        win = get_roblox_window()
        if not win:
            self.label.setText("❌ Roblox not found")
            return

        self.label.setText("⛏ Pumping...")
        perform_pump(win, PUMP_REL)
        self.label.setText("✅ Pump done")



# ----------------------------
# App Entry
# ----------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
