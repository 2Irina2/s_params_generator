import matplotlib
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from scipy import interpolate
import numpy as np

matplotlib.use('Qt5Agg')


class ResponseCanvas(FigureCanvasQTAgg):
    """
    Class responsible for rendering GraphData on a canvas and handling interaction
        - left mouse button for picking and clicking
        - scrolling wheel for zooming and point adjusting after picking
        - spacebar for default view
        - arrow keys for point adjusting after picking
        - A/D keys for navigation between points
    """

    def __init__(self, graph_data):
        figure = Figure()
        super(ResponseCanvas, self).__init__(figure)
        self.specs = None
        self.mes_data = None
        self.mes_curve = None

        self.picked_label = None
        self.picked_index = -1
        self.picked_artist = ""

        self.graph_data = graph_data
        self.axis_limits = self.make_axis_limits()
        self.axes = figure.add_subplot(111)
        self.axes.set_xlabel('Frequency(Mhz)')
        self.axes.set_ylabel('Response(' + graph_data.unit + ')')

        self.draw_specifications()
        self.draw_measurements()

        self.connect_events_to_artists()

        self.pickEvent = False

    def draw_specifications(self):
        if self.specs is not None:
            self.specs.remove()
        self.specs, = self.axes.plot(self.graph_data.frequencies, self.graph_data.specifications, 'ob-', picker=2)
        self.specs.set_label('_line0')

    def draw_measurements(self):
        if self.mes_data is not None and self.mes_curve is not None:
            self.mes_data.remove()
            self.mes_curve.remove()
        f = interpolate.interp1d(self.graph_data.measurements_x, self.graph_data.measurements_y, kind='quadratic')
        xf = np.linspace(self.graph_data.measurements_x[0], self.graph_data.measurements_x[-1], 1000)
        self.mes_data, = self.axes.plot(self.graph_data.measurements_x, self.graph_data.measurements_y, 'ro', picker=2)
        self.mes_curve, = self.axes.plot(xf, f(xf), 'r-')
        self.graph_data.set_interpolation_function(f)

    def draw_label(self, frequency, response):
        middle_frequency = self.graph_data.frequencies[int(len(self.graph_data.frequencies)/2)]
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        if self.picked_label is not None:
            self.picked_label.remove()
            self.picked_label = None
        if frequency > middle_frequency:
            label_posx = frequency + cur_xrange/15
        else:
            label_posx = frequency - cur_xrange/2
        self.picked_label = self.axes.text(label_posx, response - cur_yrange/15,
                                           str(round(frequency, 2)) + ', ' + str(round(response, 2)))
        self.picked_label.set_backgroundcolor('gray')
        self.picked_label.set_color('white')

    def connect_events_to_artists(self):
        self.specs.figure.canvas.mpl_connect('pick_event', self.onpick)
        self.specs.figure.canvas.mpl_connect('button_press_event', self.onclick)
        self.specs.figure.canvas.mpl_connect('scroll_event', self.onscroll)
        self.specs.figure.canvas.mpl_connect('key_press_event', self.onkey)

    def make_axis_limits(self):
        axis_limits = []
        x = self.graph_data.frequencies
        y = self.graph_data.specifications
        axis_limits.append(x[0] - 1000)
        axis_limits.append(x[-1] + 1000)
        axis_limits.append(min(y) - 10)
        axis_limits.append(max(y) + 10)
        return axis_limits

    def onclick(self, event):
        if event.button == MouseButton.LEFT and self.pickEvent is False:
            self.picked_index = -1
            if self.picked_label is not None:
                self.picked_label.remove()
                self.picked_label = None
            self.draw()
        self.pickEvent = False

    def onpick(self, event):
        if event.mouseevent.button == MouseButton.LEFT:
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            self.picked_index = ind[0]
            self.picked_artist = thisline.get_label()
            self.draw_label(xdata[ind[0]], ydata[ind[0]])
            self.draw()
        self.pickEvent = True

    def onscroll(self, event):
        if self.picked_index == -1:
            self.zoom(event)
        else:
            self.adjust(event.button)

    def zoom(self, event, base_scale=1.1):
        # get the current x and y limits
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
        # set new limits
        self.axes.set_xlim([xdata - cur_xrange * scale_factor,
                            xdata + cur_xrange * scale_factor])
        self.axes.set_ylim([ydata - cur_yrange * scale_factor,
                            ydata + cur_yrange * scale_factor])
        self.draw()  # force re-draw

    def adjust(self, key):
        if self.picked_artist == "_line0":
            if key == "up":
                self.graph_data.specifications[self.picked_index] = self.graph_data.specifications[
                                                                        self.picked_index] + 1
            elif key == "down":
                self.graph_data.specifications[self.picked_index] = self.graph_data.specifications[
                                                                        self.picked_index] - 1
            elif key == "right" and self.picked_index < len(self.graph_data.frequencies) - 1:
                newvalue = self.graph_data.frequencies[self.picked_index] + 10
                if newvalue >= self.graph_data.frequencies[self.picked_index + 1]:
                    self.graph_data.frequencies[self.picked_index] = self.graph_data.frequencies[
                                                                         self.picked_index + 1] - 0.1
                else:
                    self.graph_data.frequencies[self.picked_index] = newvalue
            elif key == "left" and self.picked_index > 0:
                newvalue = self.graph_data.frequencies[self.picked_index] - 10
                if newvalue <= self.graph_data.frequencies[self.picked_index - 1]:
                    self.graph_data.frequencies[self.picked_index] = self.graph_data.frequencies[
                                                                         self.picked_index - 1] + 0.1
                else:
                    self.graph_data.frequencies[self.picked_index] = newvalue
            freq = self.graph_data.frequencies[self.picked_index]
            resp = self.graph_data.specifications[self.picked_index]
            self.draw_specifications()
        elif self.picked_artist == "_line1":
            if key == "up":
                self.graph_data.measurements_y[self.picked_index] = self.graph_data.measurements_y[
                                                                        self.picked_index] + 1
            elif key == "down":
                self.graph_data.measurements_y[self.picked_index] = self.graph_data.measurements_y[
                                                                        self.picked_index] - 1
            elif key == "right" and self.picked_index < len(self.graph_data.measurements_x)-1:
                newvalue = self.graph_data.measurements_x[self.picked_index] + 10
                if newvalue >= self.graph_data.measurements_x[self.picked_index + 1]:
                    self.graph_data.measurements_x[self.picked_index] = self.graph_data.measurements_x[
                                                                            self.picked_index + 1] - 0.1
                else:
                    self.graph_data.measurements_x[self.picked_index] = newvalue
            elif key == "left" and self.picked_index > 0:
                newvalue = self.graph_data.measurements_x[self.picked_index] - 10
                if newvalue <= self.graph_data.measurements_x[self.picked_index - 1]:
                    self.graph_data.measurements_x[self.picked_index] = self.graph_data.measurements_x[
                                                                            self.picked_index - 1] + 0.1
                else:
                    self.graph_data.measurements_x[self.picked_index] = newvalue
            freq = self.graph_data.measurements_x[self.picked_index]
            resp = self.graph_data.measurements_y[self.picked_index]
            self.draw_measurements()
        else:
            freq = 0
            resp = 0
        self.draw_label(freq, resp)
        self.set_axes_limits()
        self.draw()

    def onkey(self, event):
        if event.key == ' ':
            self.axes.axis(self.axis_limits)
            self.draw()
        elif event.key == "up" or event.key == "down" or event.key == "left" or event.key == "right":
            if self.picked_index != -1:
                self.adjust(event.key)
        else:
            if self.picked_index != -1:
                self.navigate(event.key)

    def navigate(self, key):
        y = self.graph_data.specifications if self.picked_artist == "_line0" else self.graph_data.measurements_y
        x = self.graph_data.frequencies if self.picked_artist == "_line0" else self.graph_data.measurements_x
        if key == "a":
            if self.picked_index > 0:
                self.picked_index -= 1
        elif key == "d":
            if self.picked_index < len(y) - 1:
                self.picked_index += 1
        self.draw_label(x[self.picked_index], y[self.picked_index])
        self.set_axes_limits()
        # Show
        self.draw()

    def set_axes_limits(self):
        y = self.graph_data.specifications if self.picked_artist == "_line0" else self.graph_data.measurements_y
        x = self.graph_data.frequencies if self.picked_artist == "_line0" else self.graph_data.measurements_x
        # Update view
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        self.axes.set_xlim([x[self.picked_index] - cur_xrange, x[self.picked_index] + cur_xrange])
        self.axes.set_ylim([y[self.picked_index] - cur_yrange, y[self.picked_index] + cur_yrange])
