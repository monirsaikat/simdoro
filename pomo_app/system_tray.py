from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from helpers import make_icon
from helpers import mmss


class TrayController:
    """Encapsulates the system tray menu/actions."""

    def __init__(self, parent):
        self.tray = QSystemTrayIcon(make_icon(), parent)
        self.menu = QMenu()
        self.action_show = self.menu.addAction("Hide Window")
        self.action_toggle = self.menu.addAction("Start")
        self.action_reset = self.menu.addAction("Reset")
        self.menu.addSeparator()
        self.action_quit = self.menu.addAction("Quit")
        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def bind(
        self,
        *,
        on_toggle_window,
        on_toggle_timer,
        on_reset,
        on_quit,
    ) -> None:
        self.action_show.triggered.connect(on_toggle_window)
        self.action_toggle.triggered.connect(on_toggle_timer)
        self.action_reset.triggered.connect(on_reset)
        self.action_quit.triggered.connect(on_quit)

    def set_window_visible(self, visible: bool) -> None:
        self.action_show.setText("Hide Window" if visible else "Show Window")

    def update(self, running: bool, is_break: bool, remaining_seconds: int) -> None:
        mode = "Break" if is_break else "Work"
        self.tray.setToolTip(f"{mode} · {mmss(remaining_seconds)}")
        self.action_toggle.setText("Stop" if running else "Start")

    def hide(self) -> None:
        self.tray.hide()
