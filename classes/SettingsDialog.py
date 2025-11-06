from PySide6.QtWidgets import QLabel, QDialog, QGridLayout, QSpinBox, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setModal(True)

        layout = QGridLayout(self)

        layout.addWidget(QLabel('Pomodoro Time (minutes):'), 0, 0)
        self.pomodoro_time_spin_box = QSpinBox()
        self.pomodoro_time_spin_box.setRange(1, 60)
        layout.addWidget(self.pomodoro_time_spin_box, 0, 1)

        layout.addWidget(QLabel('Break Time (minutes):'), 1, 0)
        self.break_time_spin_box = QSpinBox()
        self.break_time_spin_box.setRange(1, 60)
        layout.addWidget(self.break_time_spin_box, 1, 1)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box, 2, 0, 1, 2)
    
    def get_settings(self):
        return self.pomodoro_time_spin_box.value(), self.break_time_spin_box.value()
