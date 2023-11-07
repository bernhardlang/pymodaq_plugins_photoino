from daq_0Dviewer_photoino import DAQ_0DViewer_photoino
from pymodaq.utils.parameter import Parameter
from pymodaq.control_modules.viewer_utility_classes import main
import numpy as np


class SimulatePhotoinoController:

    def __init__(self):
        self._time_base = 1.
        self._trigger_level = 0.1
        self._mean_count_rate = 100
        self._low_dark = 1000
        self._low_trigger = 0.1
        self._trigger_level = 1.0

    @property
    def time_base(self):
        return self._time_base

    @time_base.setter
    def time_base(self, value):
        self._time_base = value

    @property
    def trigger_level(self):
        return self._trigger_level

    @trigger_level.setter
    def trigger_level(self, value):
        self._trigger_level = value

    @property
    def count_rate(self):
        mean = self._mean_count_rate if self._trigger_level > self._low_trigger\
            else self._mean_count_rate + self._low_dark
        return np.random.poisson(mean)

    @property
    def mean_count_rate(self):
        return self._mean_count_rate

    @mean_count_rate.setter
    def mean_count_rate(self, value: int):
        self._mean_count_rate = int(value)

    @property
    def low_dark(self):
        return self._low_dark

    @low_dark.setter
    def low_dark(self, value: int):
        self._low_dark = int(value)

    @property
    def low_trigger(self):
        return self._low_trigger

    @low_trigger.setter
    def low_trigger(self, value: float):
        self._low_trigger = float(value)

    def start(self):
        pass

    def stop(self):
        pass

    def open(self, port, baudrate):
        pass

    def close(self):
        pass


class DAQ_0DViewer_simulate_photoino(DAQ_0DViewer_photoino):
    """PyMoDAQ plugin for simulating a photoino single-photon counting module"""

    controller_type = SimulatePhotoinoController
    params = DAQ_0DViewer_photoino.params+[
        {'title': 'Mean count rate:', 'name': 'mean_count_rate', 'type': 'int',
         'min': 0},
        {'title': 'Low trigger level dark rate:', 'name': 'low_dark',
         'type': 'int', 'min': 0},
        {'title': 'Low trigger level:', 'name': 'low_trigger', 'type': 'float',
         'min': 0},
    ]

    def init_params(self):
        DAQ_0DViewer_photoino.init_params(self)
        self.controller.mean_count_rate = self.settings['mean_count_rate']
        self.controller.low_dark = self.settings['low_dark']
        self.controller.low_trigger = self.settings['low_trigger']

    def commit_settings(self, param: Parameter):
        if param.name() == "mean_count_rate":
            self.controller.mean_count_rate = \
                self.settings.child('mean_count_rate').value()
        elif param.name() == "low_dark":
            self.controller.low_dark = \
                self.settings.child('low_dark').value()
        elif param.name() == "low_trigger":
            self.controller.low_trigger = \
                self.settings.child('low_trigger').value()
        else:
            DAQ_0DViewer_photoino.commit_settings(self, param)


if __name__ == '__main__':
    main(__file__)
