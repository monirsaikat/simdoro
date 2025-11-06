import sys

from PySide6.QtWidgets import QApplication

from pomo_app import PomodoroWindow
from pomo_app.single_instance import SingleInstanceLock


def main() -> int:
    app = QApplication(sys.argv)
    lock = SingleInstanceLock()
    try:
        lock.acquire()
    except RuntimeError as exc:
        print(exc)
        return 1

    window = PomodoroWindow(lock)
    window.resize(320, 220)
    window.show()

    try:
        return app.exec()
    finally:
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
