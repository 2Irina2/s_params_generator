from PyQt5 import QtCore, QtWidgets
import data_parser


class GraphDataQModel(QtCore.QAbstractTableModel):
    def __init__(self, graph_data, header):
        super(GraphDataQModel, self).__init__()
        self.table_data = [graph_data.frequencies, graph_data.specifications, graph_data.measurements]  # data[0] = frequencies, data[1] = specifications[, data[2] = measurements]
        self.header = header  # header = ['Frequency', 'Gain/Delay', 'Gain/Delay']

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.table_data[0])

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.table_data)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        else:
            return QtCore.QVariant(str(self.table_data[index.column()][index.row()]))

    def headerData(self, index, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[index])
        return QtCore.QVariant()


class InputScreen(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal(object)

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

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.make_center_frequency_input())
        layout.addLayout(self.make_bandwidth_input())
        tabs_widget = QtWidgets.QTabWidget()
        tabs_widget.addTab(self.make_insertion_loss_tab(), "Insertion Loss")
        tabs_widget.addTab(self.make_group_delay_tab(), "Group Delay")
        tabs_widget.addTab(self.make_input_return_loss_tab(), "Input Return Loss")
        tabs_widget.addTab(self.make_output_return_loss_tab(), "Output Return Loss")
        layout.addWidget(tabs_widget, 1, QtCore.Qt.AlignHCenter)
        layout.addWidget(self.make_finish_button(), 1, QtCore.Qt.AlignRight)

        self.setLayout(layout)

    def setup_window(self):
        self.setWindowTitle('Input')
        self.resize(700, 800)
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        qt_rectangle = self.frameGeometry()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

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

    def finish(self):
        center_frequency = self.center_frequency_line_edit.text()
        bandwidth = self.bandwidth_line_edit.text()
        loss_center_frequency = self.loss_at_center_line_edit.text()
        insertion_loss_inband = self.insertionloss_inband_text_edit.toPlainText()
        insertion_loss_outband = self.insertionloss_outofband_text_edit.toPlainText()
        group_delay_inband = self.groupdelay_inband_text_edit.toPlainText()
        group_delay_outband = self.groupdelay_outofband_text_edit.toPlainText()
        input_return = self.inputreturnloss_text_edit.toPlainText()
        output_return = self.outputreturnloss_text_edit.toPlainText()

        input_data = data_parser.InputData(center_frequency, bandwidth, loss_center_frequency, insertion_loss_inband,
                                           insertion_loss_outband, group_delay_inband, group_delay_outband,
                                           input_return,
                                           output_return)
        self.switch_window.emit(input_data)


class GenerateScreen(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self, input_data):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Generate S-parameters')

        [il_graphdata, gd_graphdata, irl_graphdata, orl_graphdata] = data_parser.make_plot_data(input_data)
        il_graphdata.set_measurements(il_graphdata.specifications)
        gd_graphdata.set_measurements(gd_graphdata.specifications)
        irl_graphdata.set_measurements(irl_graphdata.specifications)
        orl_graphdata.set_measurements(orl_graphdata.specifications)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self.make_graphs_layout(), 4)
        layout.addLayout(self.make_tabs_layout([il_graphdata, gd_graphdata, irl_graphdata, orl_graphdata]), 1)
        self.setLayout(layout)

    def make_graphs_layout(self):
        graphs = QtWidgets.QGridLayout()
        layout_g1 = QtWidgets.QVBoxLayout()
        layout_g1.addWidget(QtWidgets.QLabel('Graph1'), 1, QtCore.Qt.AlignBottom)
        layout_g1.addWidget(QtWidgets.QPushButton('Graph1'), 1, QtCore.Qt.AlignTop)
        layout_g2 = QtWidgets.QVBoxLayout()
        layout_g2.addWidget(QtWidgets.QLabel('Graph2'), 1, QtCore.Qt.AlignBottom)
        layout_g2.addWidget(QtWidgets.QPushButton('Graph2'), 1, QtCore.Qt.AlignTop)
        layout_g3 = QtWidgets.QVBoxLayout()
        layout_g3.addWidget(QtWidgets.QLabel('Graph3'), 1, QtCore.Qt.AlignBottom)
        layout_g3.addWidget(QtWidgets.QPushButton('Graph3'), 1, QtCore.Qt.AlignTop)
        layout_g4 = QtWidgets.QVBoxLayout()
        layout_g4.addWidget(QtWidgets.QLabel('Graph4'), 1, QtCore.Qt.AlignBottom)
        layout_g4.addWidget(QtWidgets.QPushButton('Graph4'), 1, QtCore.Qt.AlignTop)
        graphs.addLayout(layout_g1, 0, 0)
        graphs.addLayout(layout_g2, 0, 1)
        graphs.addLayout(layout_g3, 1, 0)
        graphs.addLayout(layout_g4, 1, 1)
        return graphs

    def make_tabs_layout(self, graph_data):
        panel = QtWidgets.QVBoxLayout()
        button_generate = QtWidgets.QPushButton('Generate')
        button_generate.clicked.connect(self.switch)

        tabs = QtWidgets.QTabWidget()
        for graph in graph_data:
            tabs.addTab(self.make_tab(graph), graph.name)
        tabs.setMinimumWidth(360)  # TODO find a better way to scale the tab on the screen

        panel.addWidget(tabs, 19, QtCore.Qt.AlignJustify)
        panel.addWidget(button_generate, 1, QtCore.Qt.AlignVCenter)
        return panel

    def make_tab(self, graph_data):
        tab = QtWidgets.QTableView()
        header = ['Frequency (Mhz)', 'Specifications (' + graph_data.unit + ')',
                  'Measurements (' + graph_data.unit + ')']
        model = GraphDataQModel(graph_data, header)
        tab.setModel(model)
        tab.verticalHeader().setVisible(False)
        tab.resizeColumnsToContents()
        return tab

    def switch(self):
        self.switch_window.emit()
