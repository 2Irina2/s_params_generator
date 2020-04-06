class InputData:
    def __init__(self, center_frequency, bandwidth, loss_center_frequency, il_inband, il_outband, gd_inband, gd_outband,
                 input_return, output_return):
        self.center_frequency = center_frequency
        self.bandwidth = bandwidth
        self.loss_center_frequency = loss_center_frequency
        self.insertion_loss_inband = il_inband
        self.insertion_loss_outofband = il_outband
        self.group_delay_inband = gd_inband
        self.group_delay_outofband = gd_outband
        self.input_return_loss = input_return
        self.output_return_loss = output_return


class OutputData:

    def __init__(self):
        print('OutputData created')
