import sys
import socket
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel, QPushButton, QHBoxLayout, QSystemTrayIcon, QDialog, QMenu
from helpers import make_icon, mmss
from classes.SettingsDialog import SettingsDialog
from sounds import play_sound

class Pomo(QWidget):
    def __init__(self):
        super().__init__()
        self.lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.lock_socket.bind(('localhost', 12345))
        except socket.error:
            print("Another instance is already running. Exiting.")
            sys.exit(1)
        
        self.minutes = 2
        self.break_minutes = 5
        self.setWindowTitle("Pomodoro")

        # --- durations (seconds) ---
        self.session_seconds = self.minutes * 60
        self.break_seconds = 5 * 60

        # --- state ---
        self.is_break = False
        self.remaining = self.session_seconds
        self.running = False

        # --- UI ---
        self.tray = QSystemTrayIcon(make_icon(), self)
        self.tray.setToolTip("Pomodoro")
        self.tray_menu = QMenu()

        self.action_show = self.tray_menu.addAction("Hide Window")
        self.action_toggle = self.tray_menu.addAction("Start")
        self.action_reset = self.tray_menu.addAction("Reset")
        
        self.tray_menu.addSeparator()
        self.action_quit = self.tray_menu.addAction("Quit")

        self.action_show.triggered.connect(self.toggle_window)
        self.action_toggle.triggered.connect(self.on_toggle)
        self.action_reset.triggered.connect(self.on_reset)
        self.action_quit.triggered.connect(self.on_quit)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()
        self.update_tray()
        
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

        # layout
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_toggle)
        btn_row.addWidget(self.btn_reset)
        btn_row.addWidget(self.btn_settings)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addLayout(btn_row)

        # --- timer ---
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)

        # connect signals
        self.btn_toggle.clicked.connect(self.on_toggle)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_settings.clicked.connect(self.on_settings)

        self.update_progress()

    def on_settings(self):
        dialog = SettingsDialog(self)
        dialog.pomodoro_time_spin_box.setValue(self.minutes)
        dialog.break_time_spin_box.setValue(self.break_minutes)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.minutes, self.break_minutes = dialog.get_settings()
            # todo: set settings with seconds for now
            self.session_seconds = self.minutes * 60
            self.break_seconds = self.break_minutes * 60
            self.remaining = self.session_seconds
            self.label.setText(mmss(self.remaining))
            self.update_progress()


    def update_tray(self):
        pass

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.action_show.setText('Show Window')

    def toggle_window(self):
        if self.isHidden():
            self.show()
            self.action_show.setText('Hide Window')
        else:
            self.hide()
            self.action_show.setText('Show Window')

    def on_quit(self):
        self.tray.hide()
        self.lock_socket.close()
        QApplication.instance().quit()
    
    def update_tray(self):
        mode = "Break" if self.is_break else "Work"
        text = f"{mode} · {mmss(self.remaining)}"
        self.tray.setToolTip(text)
        # If running → button should say "Stop", else "Start"
        self.action_toggle.setText("Stop" if self.running else "Start")


    def total_for_mode(self):
        return self.break_seconds if self.is_break else self.session_seconds

    def update_progress(self):
        total = self.total_for_mode()
        elapsed = total - self.remaining
        if elapsed < 0:
            elapsed = 0
        elif elapsed > total:
            elapsed = total

        self.progress.setValue(int(elapsed / total * 100))

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Pomo()
    w.resize(320, 220)
    w.show()
    sys.exit(app.exec())
