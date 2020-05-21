from PyQt5 import QtCore


class InputData:
    """
    Wraps response data taken from the InputScreen
    """

    def __init__(self, center_frequency, bandwidth, loss_center_frequency, il_inband, il_outband, gd_inband, gd_outband,
                 input_return, output_return):
        self.center_frequency_text = center_frequency
        self.bandwidth_text = bandwidth
        self.loss_center_frequency_text = loss_center_frequency
        self.insertion_loss_inband_text = il_inband
        self.insertion_loss_outofband_text = il_outband
        self.group_delay_inband_text = gd_inband
        self.group_delay_outofband_text = gd_outband
        self.input_return_loss_text = input_return
        self.output_return_loss_text = output_return


class NumericalData:
    """
    Wraps the plot data parsed from InputData into 4 GraphData objects for the responses
    and 3 numbers associated with the central frequency, bandwidth and loss at central frequency
    """

    def __init__(self, cf, bw, lac, il_plot, gd_plot, irl_plot, orl_plot):
        self.center_frequency = cf
        self.bandwidth = bw
        self.loss_at_center = lac
        self.insertion_loss = GraphData('Insertion Loss', 'dB', il_plot)
        self.group_delay = GraphData('Group Delay', 'ns', gd_plot)
        self.input_return_loss = GraphData('Input Loss', 'dB', irl_plot)
        self.output_return_loss = GraphData("Output Loss", 'dB', orl_plot)

    def set_graph_datas(self, il, gd, irl, orl):
        self.insertion_loss = il
        self.group_delay = gd
        self.input_return_loss = irl
        self.output_return_loss = orl


class GraphData:
    """
    Wraps plotting data used in the graphs and tabs of GenerateScreen
    """

    def __init__(self, name, unit, plot):
        self.name = name
        self.unit = unit
        self.frequencies = plot[0]
        self.specifications = plot[1]

    def set_measurements(self, measurements):
        self.measurements = measurements


class GraphDataQModel(QtCore.QAbstractTableModel):
    """
    Wraps the response graph data into a QAbstractTableModel for populating QTableView
    """

    def __init__(self, graph_data, header):
        super(GraphDataQModel, self).__init__()
        # data[0] = frequencies, data[1] = specifications[, data[2] = measurements]
        self.table_data = [graph_data.frequencies, graph_data.specifications,
                           graph_data.measurements]
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
