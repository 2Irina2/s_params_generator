import sys
import screens
from PyQt5 import QtWidgets
import configparser


class WindowController:
    """
    Defines behaviour and communication of application screens: InputScreen, GenerateScreen and SaveScreen
    """
    def __init__(self, configurations):
        self.conf = configurations
        pass

    def show_input_screen(self):
        self.input_screen = screens.InputScreen()
        self.input_screen.switch_window.connect(self.show_generate_screen)
        self.input_screen.show()

    def show_generate_screen(self, input_data, measurements_text):
        self.generate_screen = screens.GenerateScreen(input_data, measurements_text, self.conf)
        self.generate_screen.switch_window.connect(self.show_save_screen)
        self.input_screen.close()
        self.generate_screen.showMaximized()

    def show_save_screen(self, numerical_data):
        self.save_screen = screens.SaveScreen(numerical_data, self.conf['touchstone'])
        self.save_screen.exit_signal.connect(exit_application)
        self.save_screen.restart_signal.connect(self.restart_application)
        self.save_screen.cancel_signal.connect(self.cancel_save)
        self.save_screen.exec()

    def restart_application(self):
        self.conf = read_configurations()
        self.save_screen.close()
        self.generate_screen.close()
        self.show_input_screen()
        self.input_screen.show()

    def cancel_save(self):
        self.save_screen.close()


def exit_application():
    QtWidgets.QApplication.quit()


def read_configurations():
    config = configparser.ConfigParser()
    config.read('configurations.ini')
    return config


def main():
    app = QtWidgets.QApplication(sys.argv)
    configurations = read_configurations()
    controller = WindowController(configurations)
    controller.show_input_screen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
