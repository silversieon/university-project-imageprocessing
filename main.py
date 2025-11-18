import sys
from PyQt5.QtWidgets import QApplication
from view.main_view import MainView
from controller.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    view = MainView()
    controller = MainController(view)
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
