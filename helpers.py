import os
import sys
from PySide6.QtGui import QIcon, QPixmap, QPainter 
from PySide6.QtCore import Qt

def mmss(seconds: int) -> str:
    m, s = divmod(max(0, seconds), 60)
    return f"{m:02d}:{s:02d}"


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
    
def make_icon() -> QIcon:
    icon_path = resource_path('icon.png')
    icon = QIcon(icon_path)

    if not icon.isNull():
        return icon
    
    pm = QPixmap(32, 32)    
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setBrush(Qt.GlobalColor.red)
    p.setPen(Qt.GlobalColor.red)
    p.drawEllipse(4, 4, 24, 24)
    p.end()
    return QIcon(pm)
