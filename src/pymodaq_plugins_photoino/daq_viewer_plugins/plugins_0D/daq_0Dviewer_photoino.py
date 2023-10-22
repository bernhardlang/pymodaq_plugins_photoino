from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, \
    comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq.utils.data import DataFromPlugins, DataToExport

class PhotoinoController:

    pass


class DAQ_0DViewer_photoino(DAQ_Viewer_base):
    """PyMoDAQ plugin for controlling photoino single-photon counting module"""

    params = comon_parameters

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
                               new_controller=PhotoinoController)

        info = "photoino initialised"
        return info, True

    def close(self):
        """Terminate the communication protocol"""
        pass

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

        data = [np.array([0.0])]
        data_to_emit = DataFromPlugins(name='Photon counter', data=data,
                                       dim='Data0D', labels=['Counts'],)
        self.data_grabed_signal.emit([data_to_emit])

    def stop(self):
        """Device needs no stopping"""
        return ''


if __name__ == '__main__':
    main(__file__)
