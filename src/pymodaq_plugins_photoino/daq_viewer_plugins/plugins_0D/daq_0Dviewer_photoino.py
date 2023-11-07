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
        [str(path) for path in list(Path('/dev/').glob('ttyACM0'))]

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
        self.ser.write('start\n'.encode())

    def stop(self):
        self.ser.write('stop\n'.encode())

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

    @property
    def trigger_level(self):
        self.ser.write(str.encode('level?\n'))
        return self.receive_number()
        
    @trigger_level.setter
    def trigger_level(self, value):
        self.ser.write(str.encode('level %f\n' % value))


    @property
    def time_base(self):
        self.ser.write(str.encode('timebase?\n'))
        return self.receive_number()
        
    @time_base.setter
    def time_base(self, value):
        self.ser.write(str.encode('timebase %f\n' % value))


class DAQ_0DViewer_photoino(DAQ_Viewer_base):
    """PyMoDAQ plugin for controlling photoino single-photon 
       counting module"""

    controller_type = PhotoinoController
    serial_ports = PhotoinoController.available_ports

    params = comon_parameters+[
        {'title': 'Serial port:', 'name': 'serial_port', 'type': 'str',
         'limits': serial_ports },
        {'title': 'Baud rate:', 'name': 'baud_rate', 'type': 'int', 'min': 0},
        {'title': 'Time base:', 'name': 'time_base', 'type': 'float',
         'min': 0.1, 'max': 1e5},
        {'title': 'Trigger level:', 'name': 'trigger_level', 'type': 'float',
         'min': -5.0, 'max': 5.0},
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

        import pdb
        pdb.set_trace()
        self.ini_detector_init(old_controller=controller,
                               new_controller=self.controller_type())
        self.controller.open(self.settings['serial_port'],
                             self.settings['baud_rate'])

        self.init_params()

        info = "photoino initialised"
        return info, True

    def init_params(self):
        self.controller.time_base = self.settings['time_base']
        self.controller.trigger_level = self.settings['trigger_level']

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
        if param.name() == "time_base":
            self.controller.time_base = self.settings.child('time_base').value()
        elif param.name() == "trigger_level":
            self.controller.trigger_level = \
                self.settings.child('trigger_level').value()

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
        self.controller.stop()
        return ''


if __name__ == '__main__':
    main(__file__)
