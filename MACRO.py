import sys
import pyautogui
import time
import os
from AppKit import (
    NSWorkspace,
    NSApplicationActivateIgnoringOtherApps,
)


if getattr(sys, 'frozen', False):
    bundle_dir = os.path.dirname(sys.executable)
    frameworks_dir = os.path.abspath(
        os.path.join(bundle_dir, "..", "Frameworks")
    )

    qt_root = os.path.join(frameworks_dir, "PyQt6", "Qt6")

    os.environ["QT_PLUGIN_PATH"] = os.path.join(qt_root, "plugins")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
        qt_root, "plugins", "platforms"
    )

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

TIMING_BAR_REL = {
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

def switch_to_application(app_name: str) -> bool:
    workspace = NSWorkspace.sharedWorkspace()
    for app in workspace.runningApplications():
        if app.localizedName() == app_name:
            app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
            return True
    return False

# ----------------------------
# 1st minigame
# ----------------------------

def pump_points(win, rel):
    wx, wy, ww, wh = win

    # Slightly left of center of pump handle
    x = int(wx + (rel["x"] + rel["w"] * 0.45) * ww)

    y_top = int(wy + rel["y"] * wh)
    y_bottom = int(wy + (rel["y"] + rel["h"]) * wh)

    return x, y_top, y_bottom

def perform_pump(win, rel):
    x, y_top, y_bottom = pump_points(win, rel)

    switch_to_application("Roblox")
    time.sleep(0.2)
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
# 2nd minigame
# ----------------------------

def is_marker(pixel):
    r, g, b = pixel[:3]  #ignore alpha if present
    return r > 220 and g > 220 and b > 220


def is_good_zone(pixel):
    r, g, b = pixel[:3]  #ignore alpha if present
    return r > 170 and g > 150 and b < 120


def find_marker_y(img):
    pixels = img.load()
    w, h = img.size
    x = w // 2  # center of bar

    for y in range(h):
        if is_marker(pixels[x, y]):
            return y
    return None

def find_good_zone(img):
    pixels = img.load()
    w, h = img.size
    x = w // 2

    top = None
    bottom = None

    for y in range(h):
        if is_good_zone(pixels[x, y]):
            if top is None:
                top = y
            bottom = y

    if top is None:
        return None

    return top, bottom

def play_timing_minigame(win, rel, duration=6.0):
    x, y, w, h = resolve_region(win, rel)

    switch_to_application("Roblox")
    time.sleep(0.2)

    start = time.time()
    holding = False

    while time.time() - start < duration:
        img = pyautogui.screenshot(region=(x, y, w, h))

        marker_y = find_marker_y(img)
        zone = find_good_zone(img)

        if marker_y is None or zone is None:
            continue

        zone_top, zone_bottom = zone
        zone_center = (zone_top + zone_bottom) // 2

        if marker_y > zone_center + 3:
            # Marker too LOW → go UP
            print( "Marker too LOW → go UP" )
            if not holding:
                pyautogui.mouseDown()
                holding = True

        elif marker_y < zone_center - 3:
            # Marker too HIGH → go DOWN
            print( "Marker too HIGH → go DOWN" )
            if holding:
                pyautogui.mouseUp()
                holding = False

        else:
            print( "Inside zone → gentle hold" )
            # Inside zone → gentle hold
            if not holding:
                pyautogui.mouseDown()
                holding = True

        time.sleep(0.01)

    if holding:
        pyautogui.mouseUp()

def resolve_region(win, rel):
    wx, wy, ww, wh = win
    return (
        int(wx + rel["x"] * ww),
        int(wy + rel["y"] * wh),
        int(rel["w"] * ww),
        int(rel["h"] * wh),
    )


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
        self.detect_button.clicked.connect(self.test_auto_detect_2ndminigame_bar)

        self.timing_button = QPushButton("Test Timing Minigame")
        self.timing_button.clicked.connect(self.test_timing)

        self.pump_button = QPushButton("Test Pump Minigame")
        self.pump_button.clicked.connect(self.test_pump)

        layout = QVBoxLayout()
        layout.addWidget(self.pump_button)
        layout.addWidget(self.label)
        layout.addWidget(self.detect_button)
        layout.addWidget(self.timing_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def test_auto_detect_2ndminigame_bar(self):
        win = get_roblox_window()

        if not win:
            self.label.setText("❌ Roblox window not found")
            return

        region = resolve_region(win, TIMING_BAR_REL)
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

    def test_timing(self):
        win = get_roblox_window()
        if not win:
            self.label.setText("❌ Roblox not found")
            return

        self.label.setText("⏱ Stabilizing bar...")
        play_timing_minigame(win, TIMING_BAR_REL)
        self.label.setText("✅ Timing done")




# ----------------------------
# App Entry
# ----------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
