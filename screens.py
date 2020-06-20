from PyQt5 import QtCore, QtWidgets, QtGui
from datetime import datetime
import data_parser
import response_canvas
import models


class InputScreen(QtWidgets.QWidget):
    """
    Defines graphical interface for entering response data for Insertion Loss, Group Delay and (I/O) Return Loss
    Retrieves InputData and passes it to the next screen for processing
    """
    switch_window = QtCore.pyqtSignal(object, list)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.outputreturnloss_text_edit = QtWidgets.QTextEdit()
        self.inputreturnloss_text_edit = QtWidgets.QTextEdit()
        self.groupdelay_outofband_text_edit = QtWidgets.QTextEdit()
        self.groupdelay_inband_text_edit = QtWidgets.QTextEdit()
        self.insertionloss_outofband_text_edit = QtWidgets.QTextEdit()
        self.insertionloss_inband_text_edit = QtWidgets.QTextEdit()
        self.loss_at_center_line_edit = QtWidgets.QLineEdit()
        self.bandwidth_line_edit = QtWidgets.QLineEdit()
        self.center_frequency_line_edit = QtWidgets.QLineEdit()
        self.setup_window()

        self.measurements_path = None
        self.measurements_label = None

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.make_center_frequency_input())
        layout.addLayout(self.make_bandwidth_input())
        tabs_widget = QtWidgets.QTabWidget()
        tabs_widget.addTab(self.make_insertion_loss_tab(), "Insertion Loss")
        tabs_widget.addTab(self.make_group_delay_tab(), "Group Delay")
        tabs_widget.addTab(self.make_input_return_loss_tab(), "Input Return Loss")
        tabs_widget.addTab(self.make_output_return_loss_tab(), "Output Return Loss")
        layout.addWidget(tabs_widget, 1, QtCore.Qt.AlignHCenter)
        layout.addLayout(self.make_buttons_layout())

        self.set_content_debug()
        self.setLayout(layout)

    def set_content_debug(self):
        self.center_frequency_line_edit.setText("19750")
        self.bandwidth_line_edit.setText("800")
        self.loss_at_center_line_edit.setText("-1")
        il_percent = "50%     -0.2\n70%	    -0.3\n80%	    -0.45\n90%     -0.7\n100%	-1.9\n150%	-20\n175%	-30\n200%	-40"
        self.insertionloss_inband_text_edit.setText(il_percent)
        il_range = "2.520 - 8.400	-120\n10.70 - 11.50	-100\n17.30 - 17.55	-100\n17.55 - 17.80	-80\n22    - 21.20	-60\n24.75 - 25.25	-60\n27.00 - 30.00	-60\n30.00 - 31.00	-50\n37.50 - 40.00	-50\n40.00 - 48.00	-40"
        self.insertionloss_outofband_text_edit.setText(il_range)
        gd_percent = "50%     2\n90%     6\n100%	12\n150%	18\n200%	20"
        self.groupdelay_inband_text_edit.setText(gd_percent)
        gd_range = "2.520 - 8.400	30\n40.00 - 48.00   20"
        self.groupdelay_outofband_text_edit.setText(gd_range)
        irl = "2.520 - 8.400	-20\n10.70 - 11.50	-20\n17.30 - 17.55	-80\n17.55 - 17.80	-100\n22    - 21.20	-80\n24.75 - 25.25	-60\n27.00 - 30.00	-60\n30.00 - 31.00	-50\n37.50 - 40.00	-50\n40.00 - 48.00	-20"
        self.inputreturnloss_text_edit.setText(irl)
        self.outputreturnloss_text_edit.setText(irl)

    def setup_window(self):
        self.setWindowTitle('Input')
        self.resize(700, 800)
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        qt_rectangle = self.frameGeometry()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def make_buttons_layout(self):
        box = QtWidgets.QHBoxLayout()
        self.measurements_label = QtWidgets.QLabel('Measurements: None')
        self.make_measurements_button()
        box.addWidget(self.load_measurements_button, 1, QtCore.Qt.AlignLeft)
        box.addWidget(self.measurements_label, 1, QtCore.Qt.AlignCenter)
        box.addWidget(self.make_finish_button(), 1, QtCore.Qt.AlignRight)
        return box

    def select_folder(self):
        if self.measurements_path is None:
            file_dialog = QtWidgets.QFileDialog(self)
            file_dialog.setNameFilter("Text files (*.txt)")
            file_dialog.setViewMode(QtWidgets.QFileDialog.List)

            if file_dialog.exec_():
                self.measurements_path = file_dialog.selectedFiles()[0]
                self.load_measurements_button.setText("Remove measurements file")
                self.measurements_label.setText("Measurements: " + self.measurements_path)
        else:
            self.load_measurements_button.setText("Load measurements file")
            self.measurements_path = None
            self.measurements_label.setText("Measurements: None")

    def make_center_frequency_input(self):
        box = QtWidgets.QHBoxLayout()
        box.addWidget(QtWidgets.QLabel("Center frequency (Mhz): "), 1, QtCore.Qt.AlignRight)
        box.addWidget(self.center_frequency_line_edit, 1, QtCore.Qt.AlignLeft)
        return box

    def make_bandwidth_input(self):
        box = QtWidgets.QHBoxLayout()
        box.addWidget(QtWidgets.QLabel("Bandwidth (Mhz): "), 1, QtCore.Qt.AlignRight)
        box.addWidget(self.bandwidth_line_edit, 1, QtCore.Qt.AlignLeft)
        return box

    def make_loss_at_center_input(self):
        box = QtWidgets.QHBoxLayout()
        box.addWidget(QtWidgets.QLabel("Loss at center frequency (dB): "), 1, QtCore.Qt.AlignRight)
        box.addWidget(self.loss_at_center_line_edit, 1, QtCore.Qt.AlignLeft)
        box.setContentsMargins(QtCore.QMargins(2, 40, 2, 0))
        return box

    def make_insertionloss_inband_input(self):
        box = QtWidgets.QVBoxLayout()
        box.addWidget(QtWidgets.QLabel("In Band and Near Out Of Band rejection (dB): "), 1, QtCore.Qt.AlignBottom)
        self.insertionloss_inband_text_edit.setMinimumSize(200, 450)
        box.addWidget(self.insertionloss_inband_text_edit, 9, QtCore.Qt.AlignTop)
        box.setContentsMargins(QtCore.QMargins(10, 0, 5, 0))
        return box

    def make_insertionloss_outofband_input(self):
        box = QtWidgets.QVBoxLayout()
        box.addWidget(QtWidgets.QLabel("Out Of Band rejection (dB): "), 1, QtCore.Qt.AlignBottom)
        self.insertionloss_outofband_text_edit.setMinimumSize(200, 450)
        box.addWidget(self.insertionloss_outofband_text_edit, 9, QtCore.Qt.AlignTop)
        box.setContentsMargins(QtCore.QMargins(10, 0, 5, 0))
        return box

    def make_groupdelay_inband_input(self):
        box = QtWidgets.QVBoxLayout()
        box.addWidget(QtWidgets.QLabel("In band (ns): "), 1, QtCore.Qt.AlignBottom)
        self.groupdelay_inband_text_edit.setMinimumSize(200, 450)
        box.addWidget(self.groupdelay_inband_text_edit, 9, QtCore.Qt.AlignTop)
        box.setContentsMargins(QtCore.QMargins(10, 0, 5, 0))
        return box

    def make_groupdelay_outofband_input(self):
        box = QtWidgets.QVBoxLayout()
        box.addWidget(QtWidgets.QLabel("Wide band behaviour (ns): "), 1, QtCore.Qt.AlignBottom)
        self.groupdelay_outofband_text_edit.setMinimumSize(200, 450)
        box.addWidget(self.groupdelay_outofband_text_edit, 9, QtCore.Qt.AlignTop)
        box.setContentsMargins(QtCore.QMargins(10, 0, 5, 0))
        return box

    def make_insertion_loss_tab(self):
        tab = QtWidgets.QGroupBox()
        tab_content = QtWidgets.QVBoxLayout()
        tab_columns_content = QtWidgets.QHBoxLayout()
        tab_columns_content.addLayout(self.make_insertionloss_inband_input())
        tab_columns_content.addLayout(self.make_insertionloss_outofband_input())
        tab_content.addLayout(self.make_loss_at_center_input())
        tab_content.addLayout(tab_columns_content)
        tab.setLayout(tab_content)
        return tab

    def make_group_delay_tab(self):
        tab = QtWidgets.QGroupBox()
        tab_content = QtWidgets.QHBoxLayout()
        tab_content.addLayout(self.make_groupdelay_inband_input())
        tab_content.addLayout(self.make_groupdelay_outofband_input())
        tab.setLayout(tab_content)
        return tab

    def make_input_return_loss_tab(self):
        tab = QtWidgets.QGroupBox()
        tab_content = QtWidgets.QVBoxLayout()
        tab_content.addWidget(QtWidgets.QLabel("Rejection (dB): "), 1, QtCore.Qt.AlignBottom)
        self.inputreturnloss_text_edit.setMinimumSize(200, 450)
        tab_content.addWidget(self.inputreturnloss_text_edit, 9, QtCore.Qt.AlignTop)
        tab_content.setContentsMargins(QtCore.QMargins(30, 0, 30, 0))
        tab.setLayout(tab_content)
        return tab

    def make_output_return_loss_tab(self):
        tab = QtWidgets.QGroupBox()
        tab_content = QtWidgets.QVBoxLayout()
        tab_content.addWidget(QtWidgets.QLabel("Rejection (dB): "), 1, QtCore.Qt.AlignBottom)
        self.outputreturnloss_text_edit.setMinimumSize(200, 450)
        tab_content.addWidget(self.outputreturnloss_text_edit, 9, QtCore.Qt.AlignTop)
        tab_content.setContentsMargins(QtCore.QMargins(30, 0, 30, 0))
        tab.setLayout(tab_content)
        return tab

    def make_finish_button(self):
        button = QtWidgets.QPushButton('Finish')
        button.clicked.connect(self.finish)
        return button

    def make_measurements_button(self):
        self.load_measurements_button = QtWidgets.QPushButton('Load measurements file')
        self.load_measurements_button.clicked.connect(self.select_folder)

    def read_measurements_file(self):
        measurements_file = open(self.measurements_path, "r")
        text = measurements_file.readlines()
        measurements_file.close()
        return text

    def finish(self):
        if self.measurements_path is None:
            measurements_text = []
        else:
            measurements_text = self.read_measurements_file()

        # TODO handle empty inputs
        center_frequency = self.center_frequency_line_edit.text()
        bandwidth = self.bandwidth_line_edit.text()
        loss_center_frequency = self.loss_at_center_line_edit.text()
        insertion_loss_inband = self.insertionloss_inband_text_edit.toPlainText()
        insertion_loss_outband = self.insertionloss_outofband_text_edit.toPlainText()
        group_delay_inband = self.groupdelay_inband_text_edit.toPlainText()
        group_delay_outband = self.groupdelay_outofband_text_edit.toPlainText()
        input_return = self.inputreturnloss_text_edit.toPlainText()
        output_return = self.outputreturnloss_text_edit.toPlainText()

        input_data = models.InputData(center_frequency, bandwidth, loss_center_frequency, insertion_loss_inband,
                                      insertion_loss_outband, group_delay_inband, group_delay_outband,
                                      input_return,
                                      output_return)
        self.switch_window.emit(input_data, measurements_text)


class GenerateScreen(QtWidgets.QWidget):
    """
    Screen for adjusting and visualizing the frequency response graphs
    """
    switch_window = QtCore.pyqtSignal(object)

    def __init__(self, input_data, measurement_text, conf):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Generate S-parameters')

        # TODO handle empty inputs
        if input_data is not None:
            self.numerical_data = data_parser.make_plot_data(input_data, measurement_text)
            il = self.numerical_data.insertion_loss
            gd = self.numerical_data.group_delay
            irl = self.numerical_data.input_return_loss
            orl = self.numerical_data.output_return_loss
            self.graph_data_list = [il, gd, irl, orl]
        else:
            il = models.GraphData("IL", "dB", [[1, 2, 3, 4], [1, 2, 3, 4]], None)
            gd = models.GraphData("IL", "dB", [[1, 2, 3, 4], [1, 2, 3, 4]], None)
            irl = models.GraphData("IL", "dB", [[1, 2, 3, 4], [1, 2, 3, 4]], None)
            orl = models.GraphData("IL", "dB", [[1, 2, 3, 4], [1, 2, 3, 4]], None)
            self.graph_data_list = [il, gd, irl, orl]

        self.make_canvases(conf)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self.make_graphs_layout(), 4)
        layout.addLayout(self.make_tabs_layout(), 1)
        self.setLayout(layout)

    def make_canvases(self, conf):
        self.insertion_loss_canvas = response_canvas.ResponseCanvas(self.graph_data_list[0], conf['insertion_loss'])
        self.insertion_loss_canvas.graph_changed.connect(self.update_tab)
        self.insertion_loss_canvas.active_tab.connect(self.activate_tab)
        self.group_delay_canvas = response_canvas.ResponseCanvas(self.graph_data_list[1], conf['group_delay'])
        self.group_delay_canvas.graph_changed.connect(self.update_tab)
        self.group_delay_canvas.active_tab.connect(self.activate_tab)
        self.input_return_loss_canvas = response_canvas.ResponseCanvas(self.graph_data_list[2],
                                                                       conf['input_return_loss'])
        self.input_return_loss_canvas.graph_changed.connect(self.update_tab)
        self.input_return_loss_canvas.active_tab.connect(self.activate_tab)
        self.output_return_loss_canvas = response_canvas.ResponseCanvas(self.graph_data_list[3],
                                                                        conf['output_return_loss'])
        self.output_return_loss_canvas.graph_changed.connect(self.update_tab)
        self.output_return_loss_canvas.active_tab.connect(self.activate_tab)

    def make_graphs_layout(self):
        graphs = QtWidgets.QGridLayout()

        graphs.addLayout(self.make_graph(self.insertion_loss_canvas, self.graph_data_list[0].name), 0, 0)
        graphs.addLayout(self.make_graph(self.group_delay_canvas, self.graph_data_list[1].name), 0, 1)
        graphs.addLayout(self.make_graph(self.input_return_loss_canvas, self.graph_data_list[2].name), 1, 0)
        graphs.addLayout(self.make_graph(self.output_return_loss_canvas, self.graph_data_list[3].name), 1, 1)

        return graphs

    def make_graph(self, canvas, name):
        canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        canvas.setFocus()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel(name), 1, QtCore.Qt.AlignCenter)
        layout.addWidget(canvas, 9, QtCore.Qt.AlignCenter)

        return layout

    def make_tabs_layout(self):
        self.active_tab_index = 0
        panel = QtWidgets.QVBoxLayout()
        button_generate = QtWidgets.QPushButton('Generate')
        button_generate.clicked.connect(self.generate)

        self.tabs = QtWidgets.QTabWidget()
        for graph in self.graph_data_list:
            self.tabs.addTab(self.make_tab(graph), graph.name)
        self.tabs.setMinimumWidth(510)

        panel.addWidget(self.tabs, 19, QtCore.Qt.AlignJustify)
        panel.addWidget(button_generate, 1, QtCore.Qt.AlignVCenter)
        return panel

    def make_tab(self, graph_data):
        tab = QtWidgets.QGroupBox()

        tables = QtWidgets.QHBoxLayout()
        table_mes = QtWidgets.QTableView()
        header_measurements = ['Frequency (Mhz)', 'Measurements (' + graph_data.unit + ')']
        model_mes = models.GraphDataQModel(graph_data.measurements_x, graph_data.measurements_y, header_measurements)
        table_mes.setModel(model_mes)
        table_spec = QtWidgets.QTableView()
        header_specifications = ['Frequency (Mhz)', 'Specifications (' + graph_data.unit + ')']
        model_spec = models.GraphDataQModel(graph_data.frequencies, graph_data.specifications, header_specifications)
        table_spec.setModel(model_spec)

        table_mes.verticalHeader().setVisible(False)
        table_spec.verticalHeader().setVisible(False)
        table_mes.resizeColumnsToContents()
        table_spec.resizeColumnsToContents()

        tables.addWidget(table_mes, 1, QtCore.Qt.AlignJustify)
        tables.addWidget(table_spec, 1, QtCore.Qt.AlignJustify)

        tab.setLayout(tables)
        return tab

    def update_tab(self, graph_data):
        self.tabs.removeTab(self.active_tab_index)
        self.tabs.insertTab(self.active_tab_index, self.make_tab(graph_data), graph_data.name)
        self.tabs.setCurrentIndex(self.active_tab_index)

    def activate_tab(self, name):
        tabs_list = ["Insertion Loss", "Group Delay", "Input Return Loss", "Output Return Loss"]
        self.active_tab_index = tabs_list.index(name)
        self.tabs.setCurrentIndex(self.active_tab_index)

    def closeEvent(self, event):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Quit")
        msg_box.setText("Are you sure you want to quit application?")
        msg_box.setInformativeText("Data will not be saved.")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        button_reply = msg_box.exec()
        if button_reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def generate(self):
        il = self.insertion_loss_canvas.graph_data
        gd = self.group_delay_canvas.graph_data
        irl = self.input_return_loss_canvas.graph_data
        orl = self.output_return_loss_canvas.graph_data
        self.numerical_data.set_graph_datas(il, gd, irl, orl)
        self.switch_window.emit(self.numerical_data)


class SaveScreen(QtWidgets.QDialog):
    """
    Screen for generating the output and writing it to disk
    """

    exit_signal = QtCore.pyqtSignal()
    restart_signal = QtCore.pyqtSignal()
    cancel_signal = QtCore.pyqtSignal()

    def __init__(self, numerical_data, conf, parent=None):
        super(SaveScreen, self).__init__(parent)
        self.setWindowTitle("Save S-parameters and response")
        self.numerical_data = numerical_data
        self.conf = conf
        layout = QtWidgets.QVBoxLayout()

        self.filter_name_line_edit = QtWidgets.QLineEdit()
        self.absolute_losses = QtWidgets.QLineEdit()
        self.symmetry = QtWidgets.QCheckBox("")
        self.ang_s11_line_edit = QtWidgets.QLineEdit()
        self.ang_s22_line_edit = QtWidgets.QLineEdit()
        self.mag_s12_line_edit = QtWidgets.QLineEdit()
        self.ang_s12_line_edit = QtWidgets.QLineEdit()
        self.path = ""
        self.path_line_edit = QtWidgets.QLineEdit()
        self.save_and_reset_button = QtWidgets.QPushButton("Save and Reset")
        self.save_and_close_button = QtWidgets.QPushButton("Save and Close")
        self.save_and_continue_button = QtWidgets.QPushButton("Save and Continue")

        layout.addLayout(self.make_filter_name_layout(), 1)
        layout.addLayout(self.make_symmetry_layout(), 1)
        layout.addLayout(self.make_params_layout(), 1)
        layout.addLayout(self.make_path_layout(), 1)
        layout.addLayout(self.make_buttons_layout(), 1)

        self.set_debug_text()
        self.setLayout(layout)

    def set_debug_text(self):
        self.filter_name_line_edit.setText("filter")
        self.absolute_losses.setText("10")
        self.ang_s11_line_edit.setText("150")
        self.ang_s22_line_edit.setText("-60")

    def make_path_layout(self):
        box = QtWidgets.QHBoxLayout()
        button = QtWidgets.QPushButton(QtGui.QIcon("folder_icon.png"), "")
        button.clicked.connect(self.select_folder)

        self.path_line_edit.setReadOnly(True)
        self.path_line_edit.setStyleSheet("background-color: rgb(174, 174, 174);")

        box.addWidget(QtWidgets.QLabel("Save S-params and response to: "), 4, QtCore.Qt.AlignRight)
        box.addWidget(self.path_line_edit, 5, QtCore.Qt.AlignLeft)
        box.addWidget(button, 1, QtCore.Qt.AlignLeft)

        return box

    def make_filter_name_layout(self):
        box = QtWidgets.QHBoxLayout()

        box.addWidget(QtWidgets.QLabel("Name of filter: "), 4, QtCore.Qt.AlignRight)
        box.addWidget(self.filter_name_line_edit, 5, QtCore.Qt.AlignLeft)

        return box

    def make_symmetry_layout(self):
        box = QtWidgets.QHBoxLayout()

        box.addWidget(QtWidgets.QLabel("Absolute losses (dB): "), 1, QtCore.Qt.AlignRight)
        box.addWidget(self.absolute_losses, 1, QtCore.Qt.AlignLeft)
        box.addWidget(QtWidgets.QLabel("Symmetry? "), 1, QtCore.Qt.AlignRight)
        box.addWidget(self.symmetry, 1, QtCore.Qt.AlignLeft)
        self.symmetry.stateChanged.connect(self.check_symmetry)
        self.symmetry.setChecked(True)

        return box

    def check_symmetry(self, state):
        if QtCore.Qt.Checked == state:
            self.mag_s12_line_edit.clear()
            self.mag_s12_line_edit.setReadOnly(True)
            self.mag_s12_line_edit.setStyleSheet("background-color: rgb(174, 174, 174);")
            self.ang_s12_line_edit.clear()
            self.ang_s12_line_edit.setReadOnly(True)
            self.ang_s12_line_edit.setStyleSheet("background-color: rgb(174, 174, 174);")
        else:
            self.mag_s12_line_edit.setReadOnly(False)
            self.mag_s12_line_edit.setStyleSheet("background-color: white;")
            self.ang_s12_line_edit.setReadOnly(False)
            self.ang_s12_line_edit.setStyleSheet("background-color: white;")

    def make_params_layout(self):
        box = QtWidgets.QHBoxLayout()
        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()

        s11 = QtWidgets.QHBoxLayout()
        s11.addWidget(QtWidgets.QLabel("S11 phase(°): "), 1, QtCore.Qt.AlignRight)
        s11.addWidget(self.ang_s11_line_edit, 1, QtCore.Qt.AlignLeft)
        s22 = QtWidgets.QHBoxLayout()
        s22.addWidget(QtWidgets.QLabel("S22 phase(°): "), 1, QtCore.Qt.AlignRight)
        s22.addWidget(self.ang_s22_line_edit, 1, QtCore.Qt.AlignLeft)
        mags12 = QtWidgets.QHBoxLayout()
        mags12.addWidget(QtWidgets.QLabel("S12 magnitude(dB): "), 1, QtCore.Qt.AlignRight)
        mags12.addWidget(self.mag_s12_line_edit, 1, QtCore.Qt.AlignLeft)
        self.mag_s12_line_edit.setReadOnly(True)
        self.mag_s12_line_edit.setStyleSheet("background-color: rgb(174, 174, 174);")
        angs12 = QtWidgets.QHBoxLayout()
        angs12.addWidget(QtWidgets.QLabel("S12 phase(°): "), 1, QtCore.Qt.AlignRight)
        angs12.addWidget(self.ang_s12_line_edit, 1, QtCore.Qt.AlignLeft)
        self.ang_s12_line_edit.setReadOnly(True)
        self.ang_s12_line_edit.setStyleSheet("background-color: rgb(174, 174, 174);")

        left.addLayout(s11)
        left.addLayout(s22)
        right.addLayout(mags12)
        right.addLayout(angs12)
        box.addLayout(left)
        box.addLayout(right)

        return box

    def select_folder(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        file_dialog.setViewMode(QtWidgets.QFileDialog.List)

        if file_dialog.exec_():
            self.path = file_dialog.selectedFiles()[0]
            if self.path != "":
                self.path_line_edit.setText(self.path)
                self.save_and_close_button.setDisabled(False)
                self.save_and_reset_button.setDisabled(False)
                self.save_and_continue_button.setDisabled(False)

    def make_buttons_layout(self):
        box = QtWidgets.QHBoxLayout()

        self.save_and_close_button.clicked.connect(self.save_and_close)
        self.save_and_close_button.setDisabled(True)
        self.save_and_reset_button.clicked.connect(self.save_and_reset)
        self.save_and_reset_button.setDisabled(True)
        self.save_and_continue_button.clicked.connect(self.save_and_continue)
        self.save_and_continue_button.setDisabled(True)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.cancel)

        box.addWidget(self.save_and_close_button, 1, QtCore.Qt.AlignCenter)
        box.addWidget(self.save_and_reset_button, 1, QtCore.Qt.AlignCenter)
        box.addWidget(self.save_and_continue_button, 1, QtCore.Qt.AlignCenter)
        box.addWidget(cancel, 1, QtCore.Qt.AlignCenter)

        return box

    def save_and_close(self):
        self.save_data()
        self.exit_signal.emit()

    def save_and_reset(self):
        self.save_data()
        self.restart_signal.emit()

    def save_and_continue(self):
        self.save_data()
        self.cancel_signal.emit()

    def cancel(self):
        self.cancel_signal.emit()

    def save_data(self):
        self.filter_name = self.filter_name_line_edit.text()
        self.save_responses()

        absolute_losses = self.absolute_losses.text()
        ang_s11 = self.ang_s11_line_edit.text()
        ang_s22 = self.ang_s22_line_edit.text()
        mag_s12 = self.mag_s12_line_edit.text()
        ang_s12 = self.ang_s12_line_edit.text()
        sparams_data = models.SparamsData(self.numerical_data, absolute_losses, ang_s11, ang_s22, mag_s12, ang_s12,
                                          self.conf)
        sparams_lines = sparams_data.compute_parameters()
        self.save_sparams(sparams_lines)

    def save_responses(self):
        real_location = self.path + "/" + self.filter_name + "-real.txt"
        real_file = open(real_location, "w")
        self.write_real(real_file)
        real_file.close()

        ideal_location = self.path + "/" + self.filter_name + "-ideal.txt"
        ideal_file = open(ideal_location, "w")
        ideal_text_data = data_parser.make_text_data(self.numerical_data)
        ideal_file.write("\n".join(ideal_text_data))
        ideal_file.close()

    def write_real(self, real_file):
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.insertion_loss.measurements_x]) + "\n")
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.insertion_loss.measurements_y]) + "\n")
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.group_delay.measurements_x]) + "\n")
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.group_delay.measurements_y]) + "\n")
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.input_return_loss.measurements_x]) + "\n")
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.input_return_loss.measurements_y]) + "\n")
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.output_return_loss.measurements_x]) + "\n")
        real_file.write(" ".join([str(elem) for elem in self.numerical_data.output_return_loss.measurements_y]) + "\n")

    def save_sparams(self, lines):
        s_params_location = self.path + "/" + self.filter_name + "-sparams.s2p"
        s_params_file = open(s_params_location, "w")

        s_params_file.write("! Date & Time: " + str(datetime.now()) + "\n")
        s_params_file.write("! Filter name: " + self.filter_name + "\n")
        s_params_file.write("# Mhz S DB R 50\n")
        s_params_file.write("! Frequency dB(S11) ang(S11) dB(S21) ang(S21) dB(S12) ang(S12) dB(S22) ang(S22)\n")
        s_params_file.write("\n".join(lines))

        s_params_file.close()
