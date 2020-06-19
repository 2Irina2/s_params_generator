from PyQt5 import QtCore
import numpy as np
from scipy.special import binom
from scipy.integrate import cumtrapz


def take_closest(num, collection):
    return min(collection, key=lambda x: abs(x - num))


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

    def __init__(self, cf, bw, lac, il_plot, gd_plot, irl_plot, orl_plot, il_mes=None, gd_mes=None, irl_mes=None,
                 orl_mes=None):
        self.center_frequency = cf
        self.bandwidth = bw
        self.loss_at_center = lac
        self.insertion_loss = GraphData('Insertion Loss', 'dB', il_plot, il_mes)
        self.group_delay = GraphData('Group Delay', 'ns', gd_plot, gd_mes)
        self.input_return_loss = GraphData('Input Return Loss', 'dB', irl_plot, irl_mes)
        self.output_return_loss = GraphData("Output Return Loss", 'dB', orl_plot, orl_mes)

    def set_graph_datas(self, il, gd, irl, orl):
        self.insertion_loss = il
        self.group_delay = gd
        self.input_return_loss = irl
        self.output_return_loss = orl


class GraphData:
    """
    Wraps plotting data used in the graphs and tabs of GenerateScreen
    """

    def __init__(self, name, unit, specs, mes):
        self.name = name
        self.unit = unit
        self.frequencies = specs[0]
        self.specifications = specs[1]
        if mes is None:
            self.measurements_x, self.measurements_y = self.generate_measurements()
        else:
            self.measurements_x = mes[0]
            self.measurements_y = mes[1]
        self.interpolation_function = None

    def set_interpolation_function(self, f):
        self.interpolation_function = f

    def generate_measurements(self):
        """
        Automatically generates desired measurements graph based on specifications
        """
        x_bez, y_bez = self.build_bezier(list(zip(self.frequencies, self.specifications))).T
        y_bez = self.shift_bezier_outside_specs(y_bez)

        x_round = [round(num) for num in self.frequencies]
        x_unique = list(dict.fromkeys(x_round))

        xi, yi = self.map_curve_to_frequencies([x_bez, y_bez], x_unique, offset_fraction=20, sampling_threshold=3000)
        return xi, yi

    def build_bezier(self, points, num=200):
        """
        Fits a bezier curve to response specifications
        """
        N = len(points)
        t = np.linspace(0, 1, num=num)
        curve = np.zeros((num, 2))
        for ii in range(N):
            curve += np.outer(self.bernstein(N - 1, ii)(t), points[ii])
        return curve

    def bernstein(self, n, k):
        """
        Returns Bernstein polynomial function
        """
        coeff = binom(n, k)

        def _bpoly(x):
            return coeff * x ** k * (1 - x) ** (n - k)

        return _bpoly

    def shift_bezier_outside_specs(self, measurements, default_shift=1):
        """
        Bezier will be generated inside the specification graph so it needs to be shifted higher/lower
        """
        elevated = []
        specifications = np.array(self.specifications)

        threshold = 300  # safety threshold in case the interpolation introduces curves too pointy
        spec_start = specifications[0]
        spec_center = specifications[int(len(specifications) / 2)]
        peak = True if spec_center > spec_start else False  # True for functions with a max, False for fncs with a min
        if peak:
            distance = abs(measurements.max() - specifications.max())
        else:
            distance = -abs(measurements.min() - specifications.min())
        if abs(distance) < 1:
            distance = default_shift if peak else -default_shift
        if distance < threshold:
            for number in measurements:
                number += distance + distance / 10
                elevated.append(number)
        return elevated

    def map_curve_to_frequencies(self, plot, frequencies, offset_fraction=1000, sampling_threshold=1000000):
        x = plot[0]
        y = plot[1]
        xi = [x[0]]
        yi = [y[1]]
        for i in range(1, len(frequencies)):
            difference = frequencies[i] - frequencies[i - 1]
            samples = -(-difference // sampling_threshold)
            for s in range(1, samples + 1):
                freq = frequencies[i - 1] + s * sampling_threshold if frequencies[i - 1] + s * sampling_threshold < \
                                                                      frequencies[i] else frequencies[i]
                offset = 0 if frequencies[i - 1] + s * sampling_threshold < frequencies[i] \
                    else difference / offset_fraction
                if i < len(frequencies) / 2 - 1:
                    offset = -offset
                xi.append(freq + offset)
                index = np.where(x == take_closest(freq, x))
                yi.append(y[index[0][0]])
        return xi, yi


class SparamsData:

    def __init__(self, numerical_data, absolute_losses, ang_s11, ang_s22, mag_s12, ang_s12, conf):
        self.conf = conf
        self.numerical_data = numerical_data
        self.absolute_losses = float(absolute_losses)
        self.ang_s11 = ang_s11
        self.ang_s22 = ang_s22
        self.mag_s12 = None
        self.ang_s12 = None
        if mag_s12 != "" and ang_s12 != "":
            self.mag_s12 = mag_s12
            self.ang_s12 = ang_s12

    def compute_parameters(self):
        frequencies = self.numerical_data.insertion_loss.frequencies + \
                      self.numerical_data.group_delay.frequencies + \
                      self.numerical_data.input_return_loss.frequencies + \
                      self.numerical_data.output_return_loss.frequencies
        frequencies.sort()
        frequencies = list(dict.fromkeys(frequencies))
        frequencies = list(np.linspace(frequencies[0], frequencies[-1], self.conf.getint('number_of_lines')))

        irl_start_freq = self.numerical_data.input_return_loss.measurements_x[0]
        irl_end_freq = self.numerical_data.input_return_loss.measurements_x[-1]
        mag_s11_function = self.numerical_data.input_return_loss.interpolation_function

        il_start_freq = self.numerical_data.insertion_loss.measurements_x[0]
        il_end_freq = self.numerical_data.insertion_loss.measurements_x[-1]
        mag_s21_function = self.numerical_data.insertion_loss.interpolation_function

        gd_start_freq = self.numerical_data.group_delay.measurements_x[0]
        gd_start_index = frequencies.index(take_closest(gd_start_freq, frequencies))
        gd_end_freq = self.numerical_data.group_delay.measurements_x[-1]
        gd_end_index = frequencies.index(take_closest(gd_end_freq, frequencies))
        gd_function = self.numerical_data.group_delay.interpolation_function
        gd_y = gd_function(frequencies[gd_start_index:gd_end_index + 1])
        for i in range(gd_start_index):
            np.insert(gd_y, 0, gd_function(gd_start_freq))
        for i in range(gd_end_index + 1, len(frequencies)):
            np.append(gd_y, gd_function(gd_end_freq))
        phase = cumtrapz(gd_y, frequencies, initial=0)
        phase = [elem / self.conf.getfloat('group_delay_scaling') for elem in phase]

        orl_start_freq = self.numerical_data.output_return_loss.measurements_x[0]
        orl_end_freq = self.numerical_data.output_return_loss.measurements_x[-1]
        mag_s22_function = self.numerical_data.output_return_loss.interpolation_function

        lines = []
        for freq in frequencies:
            index = frequencies.index(freq)
            if freq < irl_start_freq:
                mag_s11 = mag_s11_function(irl_start_freq)
            elif freq > irl_end_freq:
                mag_s11 = mag_s11_function(irl_end_freq)
            else:
                mag_s11 = mag_s11_function(freq)
            if freq < il_start_freq:
                mag_s21 = mag_s21_function(il_start_freq)
            elif freq > il_end_freq:
                mag_s21 = mag_s21_function(il_end_freq)
            else:
                mag_s21 = mag_s21_function(freq)
            if freq < orl_start_freq:
                mag_s22 = mag_s22_function(orl_start_freq)
            elif freq > orl_end_freq:
                mag_s22 = mag_s22_function(orl_end_freq)
            else:
                mag_s22 = mag_s22_function(freq)

            line = []
            line.append(str(np.round(freq, 2)))
            line.append(str(np.round(mag_s11, 2)))
            line.append(self.ang_s11)
            line.append(str(np.round(mag_s21) - abs(self.absolute_losses)))
            line.append(str(np.round(-phase[index], 2)))
            if self.mag_s12 is None and self.ang_s12 is None:
                line.append(str(np.round(mag_s21) - abs(self.absolute_losses)))
                line.append(str(np.round(-phase[index], 2)))
            else:
                line.append(self.mag_s12)
                line.append(self.ang_s12)
            line.append(str(np.round(mag_s22, 2)))
            line.append(self.ang_s22)
            lines.append("\t".join(line))

        return lines


class GraphDataQModel(QtCore.QAbstractTableModel):
    """
    Wraps the response graph data into a QAbstractTableModel for populating QTableView
    """

    def __init__(self, frequencies, response, header):
        super(GraphDataQModel, self).__init__()
        # data[0] = frequencies, data[1] = response
        response_round = [round(num, 2) for num in response]
        self.table_data = [frequencies, response_round]
        self.header = header  # header = ['Frequency', 'Response']

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
