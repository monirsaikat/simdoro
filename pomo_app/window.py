from typing import Optional

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from classes.SettingsDialog import SettingsDialog
from helpers import mmss
from sounds import play_sound

from .single_instance import SingleInstanceLock
from .system_tray import TrayController


class PomodoroWindow(QWidget):
    """Main UI window for the Pomodoro timer."""

    def __init__(self, instance_lock: Optional[SingleInstanceLock] = None):
        super().__init__()
        self.instance_lock = instance_lock

        self.minutes = 2
        self.break_minutes = 5
        self.setWindowTitle("Pomodoro")

        self.session_seconds = self.minutes * 60
        self.break_seconds = self.break_minutes * 60

        self.is_break = False
        self.remaining = self.session_seconds
        self.running = False

        self.tray = TrayController(self)
        self.tray.bind(
            on_toggle_window=self.toggle_window,
            on_toggle_timer=self.on_toggle,
            on_reset=self.on_reset,
            on_quit=self.on_quit,
        )

        self.label = QLabel(mmss(self.remaining))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 36px;")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)

        self.btn_toggle = QPushButton("Start")
        self.btn_reset = QPushButton("Reset")
        self.btn_settings = QPushButton("Settings")

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_toggle)
        btn_row.addWidget(self.btn_reset)
        btn_row.addWidget(self.btn_settings)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addLayout(btn_row)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

        self.btn_toggle.clicked.connect(self.on_toggle)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_settings.clicked.connect(self.on_settings)

        self.update_progress()
        self.tray.set_window_visible(True)
        self.update_tray()

    def on_settings(self):
        dialog = SettingsDialog(self)
        dialog.pomodoro_time_spin_box.setValue(self.minutes)
        dialog.break_time_spin_box.setValue(self.break_minutes)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.minutes, self.break_minutes = dialog.get_settings()
            self.session_seconds = self.minutes * 60
            self.break_seconds = self.break_minutes * 60
            self.remaining = self.session_seconds
            self.label.setText(mmss(self.remaining))
            self.update_progress()
            self.update_tray()

    def toggle_window(self):
        if self.isHidden():
            self.show()
            visible = True
        else:
            self.hide()
            visible = False
        self.tray.set_window_visible(visible)

    def on_quit(self):
        self.timer.stop()
        self.tray.hide()
        if self.instance_lock:
            self.instance_lock.release()
        QApplication.instance().quit()

    def closeEvent(self, event):
        self.on_quit()
        event.accept()

    def total_for_mode(self) -> int:
        return self.break_seconds if self.is_break else self.session_seconds

    def update_progress(self):
        total = self.total_for_mode()
        elapsed = total - self.remaining
        elapsed = max(0, min(elapsed, total))
        self.progress.setValue(int(elapsed / total * 100))

    def update_tray(self):
        self.tray.update(self.running, self.is_break, self.remaining)
        self.tray.set_window_visible(not self.isHidden())

    def tick(self):
        self.remaining -= 1
        self.label.setText(mmss(self.remaining))
        self.update_progress()

        if self.remaining <= 0:
            play_sound()
            self.timer.stop()
            self.running = False
            self.btn_toggle.setText("Start")
            self.is_break = not self.is_break
            self.remaining = self.break_seconds if self.is_break else self.session_seconds
            self.label.setText("Break!" if self.is_break else "Work!")
            self.update_progress()
        self.update_tray()

    def on_toggle(self):
        if not self.running:
            self.running = True
            self.btn_toggle.setText("Stop")
            self.timer.start()
        else:
            self.running = False
            self.btn_toggle.setText("Start")
            self.timer.stop()
        self.update_tray()

    def on_reset(self):
        self.timer.stop()
        self.running = False
        self.remaining = self.break_seconds if self.is_break else self.session_seconds
        self.label.setText(mmss(self.remaining))
        self.btn_toggle.setText("Start")
        self.update_progress()
        self.update_tray()
