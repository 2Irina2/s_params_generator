import matplotlib
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')


# TODO Solve maximum recursion depth exceeding while calling a Python object (not valid anymore??)
class ResponseCanvas(FigureCanvasQTAgg):

    def __init__(self, graph_data):
        figure = Figure()
        super(ResponseCanvas, self).__init__(figure)
        self.picked_label = None
        self.picked_index = -1
        self.graph_data = graph_data
        self.axis_limits = self.make_axis_limits()

        self.axes = figure.add_subplot(111)
        self.specs, = self.axes.plot(self.graph_data.frequencies, self.graph_data.specifications, 'or-', picker=2)

        self.specs.figure.canvas.mpl_connect('pick_event', self.onpick)
        self.specs.figure.canvas.mpl_connect('button_press_event', self.onclick)
        self.specs.figure.canvas.mpl_connect('scroll_event', self.onscroll)
        self.specs.figure.canvas.mpl_connect('key_press_event', self.onkey)

        self.pickEvent = False

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
            if self.picked_label is not None:
                self.picked_label.remove()
            self.picked_label = self.axes.text(xdata[ind] + 0.5, ydata[ind] + 0.5,
                                               str(xdata[ind[0]]) + ' ' + str(ydata[ind[0]]))
            self.draw()
        self.pickEvent = True

    def onscroll(self, event):
        if self.picked_index == -1:
            self.zoom(event)
        else:
            self.adjust(event.button)

    def zoom(self, event, base_scale=2):
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
        if key == "up":
            self.graph_data.specifications[self.picked_index] = self.graph_data.specifications[self.picked_index] + 1
        elif key == "down":
            self.graph_data.specifications[self.picked_index] = self.graph_data.specifications[self.picked_index] - 1
        freq = self.graph_data.frequencies[self.picked_index]
        spec = self.graph_data.specifications[self.picked_index]
        self.axes.clear()
        self.picked_label = self.axes.text(freq + 0.5, spec + 0.5, str(freq) + " " + str(spec))
        self.specs, = self.axes.plot(self.graph_data.frequencies, self.graph_data.specifications, 'or-', picker=2)
        self.draw()

    def onkey(self, event):
        if event.key == ' ':
            self.axes.axis(self.axis_limits)
            self.draw()
        elif event.key == "up" or event.key == "down":
            if self.picked_index != -1:
                self.adjust(event.key)
        else:
            if self.picked_index != -1:
                self.navigate(event.key)

    def navigate(self, key):
        y = self.graph_data.specifications
        x = self.graph_data.frequencies
        if key == "left":
            if self.picked_index > 0:
                self.picked_index -= 1
        elif key == "right":
            if self.picked_index < len(y) - 1:
                self.picked_index += 1
        # Update label
        if self.picked_label is not None:
            self.picked_label.remove()
        self.picked_label = self.axes.text(x[self.picked_index] + 0.5, y[self.picked_index] + 0.5,
                                           str(x[self.picked_index]) + " " + str(y[self.picked_index]))
        # Update view
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        self.axes.set_xlim([x[self.picked_index] - cur_xrange, x[self.picked_index] + cur_xrange])
        self.axes.set_ylim([y[self.picked_index] - cur_yrange, y[self.picked_index] + cur_yrange])
        # Show
        self.draw()
