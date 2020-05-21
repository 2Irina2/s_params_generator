import io
import models


#################################### InputData to NumericalData #############################################

def get_numerical_data_from_text(text, negative=-1):
    """
    Parses the text given in the input screen and returns data that can be easily processed

    :param text: The text to be parsed
    :param negative: Adds the '-' back to negative numbers. -1 by default. Must be set to 1 if parsing Group Delay text.
    :return: list of tuples (one for each line) containing the numeric values
    """
    values = []
    text = io.StringIO(text)
    for line in text.readlines():
        line = line.replace('-', ' ')
        splits = line.split()
        if len(splits) == 2:  # Parsing percent data
            values.append((int(splits[0][:-1]), negative * float(splits[1])))
        elif len(splits) == 3:  # Parsing range data
            values.append(((float(splits[0]), float(splits[1])), negative * float(splits[2])))
        else:  # Incorrect format, it can occur on any line of the file
            print("Incorrect format: " + line)
            exit()

    return values


def get_numerical_data_from_input_data(input_data):
    """
    Parses all text fields from input data
    :param input_data: The InputData object containing all text fields
    :return: The list of numerical values corresponding to the text input fields
    """
    center_frequency = int(input_data.center_frequency_text)
    bandwidth = int(input_data.bandwidth_text)
    loss_center_frequency = float(input_data.loss_center_frequency_text)

    insertion_loss_percent = get_numerical_data_from_text(input_data.insertion_loss_inband_text)
    insertion_loss_range = get_numerical_data_from_text(input_data.insertion_loss_outofband_text)
    group_delay_percent = get_numerical_data_from_text(input_data.group_delay_inband_text, negative=1)
    group_delay_range = get_numerical_data_from_text(input_data.group_delay_outofband_text, negative=1)
    input_return_range = get_numerical_data_from_text(input_data.input_return_loss_text)
    output_return_range = get_numerical_data_from_text(input_data.output_return_loss_text)

    return center_frequency, bandwidth, loss_center_frequency, insertion_loss_percent, insertion_loss_range, \
           group_delay_percent, group_delay_range, input_return_range, output_return_range


def make_plot_data(input_data):
    """
    Transforms given InputData object into GraphData objects for each of the 4 graphs
    :param input_data: InputData object containing the text input
    :return: 4 GraphData objects for Insertion Loss, Group Delay and Return Loss as well as the
             3 response features (center frequency, bandwidth, loss at center frequency)
    """
    cf, bw, loss_cf, il_percent, il_range, gd_percent, gd_range, irl_range, orl_range = \
        get_numerical_data_from_input_data(input_data)

    il_plot = get_plot_insertionloss_groupdelay(cf, bw, il_percent, il_range, loss_center=loss_cf)
    gd_plot = get_plot_insertionloss_groupdelay(cf, bw, gd_percent, gd_range)
    irl_plot = get_plot_returnloss(cf, irl_range)
    orl_plot = get_plot_returnloss(cf, orl_range)

    return models.NumericalData(cf, bw, loss_cf, il_plot, gd_plot, irl_plot, orl_plot)


def get_plot_insertionloss_groupdelay(center_frequency, bandwidth, percent_contents, range_contents, loss_center=None):
    """
    Creates data for plotting Insertion Loss or Group delay
    :param center_frequency: The central frequency
    :param bandwidth:  The bandwidth
    :param percent_contents: The numerical percent information for in band behaviour
    :param range_contents: The numerical range information for out of band behaviour
    :param loss_center: The loss at central frequency. Default is None for Group Delay. Must be set for Insertion Loss
    :return: The 2D array with the frequency vector on first position and the value vector on the second position
    """
    before_central_plot, after_central_plot = make_plot_from_range(center_frequency, range_contents)
    in_range_plot = make_plot_from_percent(center_frequency, bandwidth, percent_contents, loss_center)
    result = connect_percent_range_plot(before_central_plot, in_range_plot, after_central_plot)

    return result


def get_plot_returnloss(center_frequency, range_contents):
    """
    Creates data for plotting Input and Output Return Loss
    :param center_frequency: The central frequency
    :param range_contents: The numerical range information for out of band behaviour
    :return: The 2D array with the frequency vector on first position and the value vector on the second position
    """
    range_data_before, range_data_after = make_plot_from_range(center_frequency, range_contents)
    result = connect_range_plot(center_frequency, range_data_before, range_data_after)

    return result


def make_plot_from_range(center_frequency, range_data):
    before_central_frequency = []
    after_central_frequency = []
    before_central_response = []
    after_central_response = []
    for index in range(0, len(range_data) - 1):
        point = range_data[index]
        next_point = range_data[index + 1]

        start_frequency = point[0][0] * 1000
        end_frequency = point[0][1] * 1000
        if start_frequency < center_frequency:
            before_central_frequency.append(start_frequency)
            before_central_response.append(point[1])
            start_frequency_next_point = next_point[0][0] * 1000
            if start_frequency_next_point < center_frequency:
                before_central_frequency.append(start_frequency_next_point - 0.001)
                before_central_response.append(point[1])
        else:
            after_central_frequency.append(end_frequency)
            after_central_response.append(point[1])
            after_central_frequency.append(end_frequency + 0.001)
            after_central_response.append(next_point[1])
    last_point = range_data[-1]
    after_central_frequency.append(last_point[0][1] * 1000)
    after_central_response.append(last_point[1])
    return (before_central_frequency, before_central_response), (after_central_frequency, after_central_response)


def make_plot_from_percent(center_frequency, bandwidth, percent_data, loss_center=None):
    inrange_frequency = [center_frequency]
    if loss_center is not None:
        inrange_response = [loss_center + percent_data[0][1]]
    else:
        inrange_response = [0]
    for index in range(0, len(percent_data)):
        point = percent_data[index]
        # Frequency list
        current_frequency = point[0]
        plus_frequency = center_frequency + current_frequency / 200 * bandwidth
        minus_frequency = center_frequency - current_frequency / 200 * bandwidth
        if index != 0:
            inrange_frequency.append(inrange_frequency[-1] + 0.001)
            inrange_frequency.insert(0, inrange_frequency[0] - 0.001)
        inrange_frequency.append(plus_frequency)
        inrange_frequency.insert(0, minus_frequency)
        # Rejection list
        current_rejection = point[1]
        if current_frequency <= 100 and loss_center is not None:
            current_rejection += loss_center
        if index != 0:
            inrange_response.append(current_rejection)
            inrange_response.insert(0, current_rejection)
        inrange_response.append(current_rejection)
        inrange_response.insert(0, current_rejection)
    return inrange_frequency, inrange_response


def connect_percent_range_plot(before_range_plot, in_range_plot, after_range_plot):
    final_plot_frequency = []
    final_plot_response = []

    final_plot_frequency.extend(before_range_plot[0])
    final_plot_frequency.append(in_range_plot[0][0] - 0.001)
    final_plot_frequency.extend(in_range_plot[0])
    final_plot_frequency.append(in_range_plot[0][-1] + 0.001)
    final_plot_frequency.extend(after_range_plot[0])

    final_plot_response.extend(before_range_plot[1])
    final_plot_response.append(before_range_plot[1][-1])
    final_plot_response.extend(in_range_plot[1])
    final_plot_response.append(after_range_plot[1][0])
    final_plot_response.extend(after_range_plot[1])

    return final_plot_frequency, final_plot_response


def connect_range_plot(central_frequency, before_range_plot, after_range_plot):
    final_plot_frequency = []
    final_plot_response = []

    final_plot_frequency.extend(before_range_plot[0])
    final_plot_frequency.append(central_frequency - 0.001)
    final_plot_frequency.append(central_frequency)
    final_plot_frequency.extend(after_range_plot[0])

    final_plot_response.extend(before_range_plot[1])
    final_plot_response.append(before_range_plot[1][-1])
    final_plot_response.append(after_range_plot[1][0])
    final_plot_response.extend(after_range_plot[1])

    return final_plot_frequency, final_plot_response


######################################## NumericalData to text ##########################################


def make_text_data(numerical_data):
    """
    Transforms given NumericalData object into text objects for each of the 4 graphs
    :param numerical_data: NumericalData object containing the GraphData objects and graph features
    :return: array of 4 text objects, one for each response
    """
    cf = numerical_data.center_frequency
    bw = numerical_data.bandwidth
    lac = numerical_data.loss_at_center
    il = numerical_data.insertion_loss
    gd = numerical_data.group_delay
    irl = numerical_data.input_return_loss
    orl = numerical_data.output_return_loss

    il_percent_contents, il_range_contents = get_percent_and_range(cf, bw, [il.frequencies, il.specifications], lac)
    gd_percent_contents, gd_range_contents = get_percent_and_range(cf, bw, [gd.frequencies, gd.specifications])
    irl_plot = remove_redundant_plot_points(cf, [irl.frequencies, irl.specifications])
    irl_range_contents = make_range_from_plot_data(cf, bw, irl_plot)
    orl_plot = remove_redundant_plot_points(cf, [orl.frequencies, orl.specifications])
    orl_range_contents = make_range_from_plot_data(cf, bw, orl_plot)

    il_text = write_contents_to_string(il.name, il_range_contents, cf, bw, il_percent_contents, lac)
    gd_text = write_contents_to_string(gd.name, gd_range_contents, cf, bw, gd_percent_contents)
    irl_text = write_contents_to_string(irl.name, irl_range_contents, cf, bw)
    orl_text = write_contents_to_string(orl.name, orl_range_contents, cf, bw)

    return [il_text, gd_text, irl_text, orl_text]


def get_percent_and_range(center_frequency, bandwidth, plot, loss_center=None):
    """
    For given plot data generate text output compatible with the InputData format
    :param center_frequency: the central frequency
    :param bandwidth: the response bandwidth
    :param plot: the plot data containing frequencies and specifications
    :param loss_center: the loss at central frequency. Default is none. Makes sense only for Insertion Loss graph
    :return 2 blocks of text corresponding to the percentage, respectively range inputs
    """
    plot = remove_redundant_plot_points(center_frequency, plot)
    frequencies = plot[0]
    response = plot[1]

    min_percent_ind = frequencies.index(center_frequency - bandwidth)
    max_percent_ind = frequencies.index(center_frequency + bandwidth)
    percent_plot = (frequencies[min_percent_ind:max_percent_ind + 1], response[min_percent_ind:max_percent_ind + 1])
    range_plot = (frequencies[:min_percent_ind] + frequencies[max_percent_ind + 1:],
                  response[:min_percent_ind] + response[max_percent_ind + 1:])

    percent_contents = make_percent_from_plot_data(center_frequency, bandwidth, percent_plot, loss_center=loss_center)
    range_contents = make_range_from_plot_data(center_frequency, bandwidth, range_plot)

    return percent_contents, range_contents


def remove_redundant_plot_points(center_frequency, plot):
    center_index = plot[0].index(center_frequency)
    x = remove_redundant_list_elements(center_index, plot[0])
    y = remove_redundant_list_elements(center_index, plot[1])
    return x, y


def remove_redundant_list_elements(center_index, list_to_clean):
    clean_list = []
    clean_list.extend(list_to_clean[:center_index][::2])
    clean_list.extend(list_to_clean[center_index + 1:][::2])
    return clean_list


# TODO: update loss at center if value for 50% is greater than 1
def make_percent_from_plot_data(center_frequency, bandwidth, plot, loss_center=None):
    contents = []
    for index in range(0, int(len(plot[0]) / 2)):
        current_percentage = (center_frequency - plot[0][index]) * 200 / bandwidth
        current_rejection = plot[1][index]
        if loss_center is not None and current_percentage <= 100:
            current_rejection -= loss_center
        contents.append((int(current_percentage), round(current_rejection, 2)))
    contents.reverse()
    return contents


def make_range_from_plot_data(center_frequency, bandwidth, plot):
    contents = []
    frequencies = plot[0]
    for index in range(0, len(frequencies)):
        if frequencies[index] < center_frequency:
            if index + 1 == len(frequencies):
                return contents
            if frequencies[index + 1] < center_frequency:
                contents.append(((frequencies[index] / 1000, frequencies[index + 1] / 1000), plot[1][index]))
            else:
                contents.append(((frequencies[index] / 1000, (center_frequency - bandwidth) / 1000), plot[1][index]))
        else:
            if index == 0:
                continue
            if frequencies[index - 1] > center_frequency:
                contents.append(((frequencies[index - 1] / 1000, frequencies[index] / 1000), plot[1][index]))
            else:
                contents.append((((center_frequency + bandwidth) / 1000, frequencies[index] / 1000), plot[1][index]))
    return contents


def write_contents_to_string(title, range_contents, center_frequency, bandwidth, percent_contents=None,
                             loss_at_center=None):
    """
    Compiles all text information for one graph into one block
    :param title: the name of the response
    :param range_contents: the text block for range specification
    :param center_frequency: the central frequency
    :param bandwidth: the bandwidth
    :param percent_contents: the text block for percent specification. Default is none (for IRL and ORL)
    :param loss_at_center: the loss at central frequency. Default is none. Makes sense only for Insertion Loss graph
    :return: One block of text containing the information for the graph
    """
    string_list = [title + "\n", "Center frequency: " + str(center_frequency) + "\n",
                   "Bandwidth: " + str(bandwidth) + "\n"]
    if loss_at_center is not None:
        string_list.append("Loss at center frequency: " + str(loss_at_center) + "\n")
    if percent_contents is not None:
        string_list.append("In band:\n")
        for content in percent_contents:
            string_list.append(str(content[0]) + '%    ' + str(content[1]) + "\n")
    string_list.append("\n")
    string_list.append("Out of band:\n")
    for content in range_contents:
        string_list.append(str(content[0][0]) + " - " + str(content[0][1]) + "  " + str(content[1]) + "\n")
    return ''.join(string_list)
