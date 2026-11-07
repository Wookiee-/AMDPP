import json
import os
import subprocess
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

DBUS_DEST = "org.freedesktop.UPower.PowerProfiles"
DBUS_PATH = "/org/freedesktop/UPower/PowerProfiles"
EPP_FILE = "/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference"
EPP_HELPER = "/usr/lib/amdpp/set-epp"
ICON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "amd.png")
STATE_FILE = os.path.join(os.path.expanduser("~"), ".config", "power-tray", "state.json")

PROFILES = [
    ("power-saver", "Power Saver"),
    ("balanced", "Balanced"),
    ("performance", "Performance"),
]
EPPS = ["power", "balance_power", "balance_performance", "performance", "default"]


def get_profile():
    out = subprocess.run(
        ["busctl", "--system", "get-property", DBUS_DEST, DBUS_PATH, DBUS_DEST, "ActiveProfile"],
        capture_output=True,
        text=True,
    ).stdout
    return out.strip().split('"')[1] if '"' in out else ""


def set_profile(name):
    subprocess.run(
        ["busctl", "--system", "set-property", DBUS_DEST, DBUS_PATH, DBUS_DEST, "ActiveProfile", "s", name],
        check=False,
    )


def get_epp():
    try:
        with open(EPP_FILE) as f:
            return f.read().strip()
    except OSError:
        return ""


def set_epp(value):
    if subprocess.run(["sudo", "-n", EPP_HELPER, value]).returncode != 0:
        subprocess.run(["pkexec", EPP_HELPER, value])


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(**values):
    state = load_state()
    state.update(values)
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


class PowerTray:
    def __init__(self, app):
        self.app = app
        self.tray = QSystemTrayIcon()
        self.menu = QMenu()
        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip("AMDPP")

        self.status_action = QAction("AMDPP", self.menu, enabled=False)
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()

        self.profile_group = QActionGroup(self.menu)
        self.profile_actions = {}
        for pid, label in PROFILES:
            action = QAction(label, self.menu, checkable=True)
            action.triggered.connect(lambda checked=False, p=pid: self.on_profile(p))
            self.profile_group.addAction(action)
            self.menu.addAction(action)
            self.profile_actions[pid] = action

        self.menu.addSeparator()
        self.epp_menu = self.menu.addMenu("Energy preference")
        self.epp_group = QActionGroup(self.epp_menu)
        self.epp_actions = {}
        for value in EPPS:
            action = QAction(value, self.epp_menu, checkable=True)
            action.triggered.connect(lambda checked=False, v=value: self.on_epp(v))
            self.epp_group.addAction(action)
            self.epp_menu.addAction(action)
            self.epp_actions[value] = action

        self.menu.addSeparator()
        quit_action = QAction("Quit", self.menu)
        quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(quit_action)

        self.tray.show()
        self.restore()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)
        self.refresh()

    def restore(self):
        state = load_state()
        profile = state.get("profile")
        if profile and profile != get_profile():
            set_profile(profile)
        epp = state.get("epp")
        if epp:
            self.restore_attempts = 10
            self.restore_timer = QTimer()
            self.restore_timer.timeout.connect(lambda: self.enforce_epp(epp))
            self.restore_timer.start(2000)

    def enforce_epp(self, epp):
        self.restore_attempts -= 1
        if get_epp() != epp:
            subprocess.run(["sudo", "-n", EPP_HELPER, epp])
        if self.restore_attempts <= 0:
            self.restore_timer.stop()

    def on_profile(self, name):
        set_profile(name)
        save_state(profile=name)
        self.refresh()

    def on_epp(self, value):
        set_epp(value)
        save_state(epp=value)
        self.refresh()

    def refresh(self):
        profile = get_profile()
        epp = get_epp()

        for pid, action in self.profile_actions.items():
            action.setChecked(pid == profile)

        for value, action in self.epp_actions.items():
            action.setChecked(value == epp)

        self.tray.setIcon(QIcon(ICON_FILE))
        status = f"AMDPP: {profile or 'unknown'} / EPP {epp or 'unknown'}"
        self.tray.setToolTip(status)
        self.status_action.setText(status)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AMDPP")
    app.setApplicationDisplayName("AMDPP")
    app.setQuitOnLastWindowClosed(False)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("No system tray available", file=sys.stderr)
        return 1
    PowerTray(app)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
