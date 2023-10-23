from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, \
    comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq.utils.data import DataFromPlugins, DataToExport
import numpy as np


class PhotoinoController:
    """Controller class for interacting with photoino simulation."""

    def __init__(self):
        self._timebase = 1.
        self._mean_count_rate = 100

    @property
    def timebase(self):
        return self._timebase

    @timebase.setter
    def timebase(self, value):
        self._timebase = value

    @property
    def count_rate(self):
        return np.random.poisson(self._mean_count_rate)

    @property
    def mean_count_rate(self):
        return self._mean_count_rate

    @mean_count_rate.setter
    def mean_count_rate(self, value: int):
        if value < 0:
            raise ValueError("count rate must be a positive number")
        self._mean_count_rate = int(value)


class DAQ_0DViewer_photoino(DAQ_Viewer_base):
    """PyMoDAQ plugin for controlling photoino single-photon counting module"""

    params = comon_parameters+[
        {'title': 'Timebase:', 'name': 'timebase', 'type': 'float', 'min': 0.1,
         'max': 1e5},
        {'title': 'Mean count rate:', 'name': 'mean_count_rate', 'type': 'int',
         'min': 0},
    ]

    def ini_attributes(self):
        self.controller: PhotoinoDriver = None


    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one 
            actuator/detector by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        self.ini_detector_init(old_controller=controller,
                               new_controller=PhotoinoController())

        self.controller.timebase = self.settings['timebase']
        self.controller.mean_count_rate = self.settings['mean_count_rate']

        info = "photoino initialised"
        return info, True

    def close(self):
        """Terminate the communication protocol"""
        pass

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been 
            changed by the user
        """
        if param.name() == "timebase":
            self.controller.timebase = \
                self.settings.child('timebase').value()
        elif param.name() == "mean_count_rate":
            self.controller.mean_count_rate = \
                self.settings.child('mean_count_rate').value()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, 
            self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """

        data = [np.array([self.controller.count_rate])]
        data_to_emit = DataFromPlugins(name='Photon counter', data=data,
                                       dim='Data0D', labels=['Counts'],)
        self.data_grabed_signal.emit([data_to_emit])

    def stop(self):
        """Device needs no stopping"""
        return ''


if __name__ == '__main__':
    main(__file__)
