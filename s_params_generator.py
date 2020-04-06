import sys
import window_controller
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = window_controller.WindowController()
    controller.show_generate_screen(None)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
