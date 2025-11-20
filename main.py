import sys
from PyQt5.QtWidgets import QApplication
from app_manager import AppManager

def main():
    app = QApplication(sys.argv)
    manager = AppManager()
    manager.show_start_screen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
