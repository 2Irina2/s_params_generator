from PyQt5 import QtWidgets
import screens


class SaveScreen(QtWidgets.QWidget):

    def __init__(self, text):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Save plots and S-parameters')

        layout = QtWidgets.QGridLayout()

        self.label = QtWidgets.QLabel(text)
        layout.addWidget(self.label)

        self.button = QtWidgets.QPushButton('Close')
        self.button.clicked.connect(self.close)

        layout.addWidget(self.button)

        self.setLayout(layout)


class WindowController:

    def __init__(self):
        self.input_screen = screens.InputScreen()

    def show_input_screen(self):
        self.input_screen.switch_window.connect(self.show_generate_screen)
        self.input_screen.show()

    def show_generate_screen(self, input_data):
        self.generate_screen = screens.GenerateScreen(input_data)
        self.generate_screen.switch_window.connect(self.show_save_screen)
        self.input_screen.close()
        self.generate_screen.showMaximized()

    def show_save_screen(self, text):
        self.save_screen = SaveScreen("qwertyu")
        self.generate_screen.close()
        self.save_screen.show()
