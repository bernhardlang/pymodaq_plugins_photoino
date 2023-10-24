from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, \
    comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq.utils.data import DataFromPlugins, DataToExport
import numpy as np
from pathlib import Path
import serial


class PhotoinoController:
    """Controller class for interacting with photoino."""

    available_ports = \
        [str(path) for path in list(Path('/dev/').glob('ttyACM*'))]

    def open(self, port, baudrate):
        if port == '':
            port = self.available_ports[0]
        if baudrate == 0:
            baudrate = 115200

        if hasattr(self, 'ser') and self.ser is not None:
            self.ser.close()

        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        except:
            self.ser = None
            raise ValueError("couldn't open port '%s'" % port)

    def close(self):
        if self.ser is not None:
            self.stop()
            self.ser.close()
            self.ser = None

    def start(self):
        self.ser.write(r'start\n')

    def stop(self):
        self.ser.write(r'stop\n')

    def receive_number(self):
        while True: # skip leading line breaks
            c = self.ser.read(1)
            if c != b'\n' and c != b'\r':
                break
        result = 0
        while c != b'\n' and c != b'\r':
            result = result * 10 + int(c)
            c = self.ser.read(1)
        n = self.ser.in_waiting # skip trailing stuff
        if n > 0:
            self.ser.read(n)
        return result

    @property
    def count_rate(self):
        self.ser.write(str.encode('rate?\n'))
        return self.receive_number()


class SimulatePhotoinoController:

    def __init__(self):
        self._timebase = 1.
        self._trigger_level = 0.1
        self._mean_count_rate = 100

    @property
    def timebase(self):
        return self._timebase

    @timebase.setter
    def timebase(self, value):
        self._timebase = value

    @property
    def trigger_level(self):
        return self._trigger_level

    @trigger_level.setter
    def trigger_level(self, value):
        self._trigger_level = value

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

    def start(self):
        pass

    def stop(self):
        pass


class DAQ_0DViewer_photoino(DAQ_Viewer_base):
    """PyMoDAQ plugin for controlling photoino single-photon counting module"""

    serial_ports = PhotoinoController.available_ports

    params = comon_parameters+[
        {'title': 'Serial port:', 'name': 'serial_port', 'type': 'str',
         'limits': serial_ports },
        {'title': 'Baudrate:', 'name': 'baudrate', 'type': 'int', 'min': 0},
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

        self.controller.open(self.settings['serial_port'],
                             self.settings['baudrate'])

        info = "photoino initialised"
        return info, True

    def close(self):
        self.controller.close()

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been 
            changed by the user
        """
        pass # nothing to be passed to the board yet

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
        self.controller.stop_grabbing()
        return ''


class DAQ_0DViewer_simulate_photoino(DAQ_0DViewer_photoino):
    """PyMoDAQ plugin for simulating a photoino single-photon counting module"""

    params = DAQ_0DViewer_photoino.params+[
        {'title': 'Mean count rate:', 'name': 'mean_count_rate', 'type': 'int',
         'min': 0},
    ]

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
                               new_controller=SimulatePhotoinoController())

        self.controller.mean_count_rate = self.settings['mean_count_rate']

        info = "photoino initialised"
        return info, True

    def commit_settings(self, param: Parameter):
        if param.name() == "mean_count_rate":
            self.controller.mean_count_rate = \
                self.settings.child('mean_count_rate').value()
        else:
            DAQ_0DViewer_photoino.commit_settings(self, param)


if __name__ == '__main__':
    main(__file__)
