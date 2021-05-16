import numpy as np


class Satellite:
    """
    This class holds all the information about a single satellite.


    Parameters
    ----------
    name: str
    kepler_ellipse: KeplerEllipse
    """

    def __init__(self, name, kepler_ellipse, offset):
        self.name = name
        self.kepler_ellipse = kepler_ellipse
        self.offset = offset
        current_position = self.kepler_ellipse.xyzPos(self.offset)
        self.x_position = current_position[0]
        self.y_position = current_position[1]
        self.z_position = current_position[2]

    def set_new_position(self, current_time):
        """
        Sets the new position of a satellite.
        It calls xyzPos from PyAstronomy KeplerEllipse. The parameter for this function is the time.
        Therefore, we have to add the current time to the offset (the initial position of the satellite)

        Parameters
        ----------
        current_time : int
            new time to calculate the new position

        Returns
        -------

        """
        updated_position = self.kepler_ellipse.xyzPos(current_time + self.offset)
        self.x_position = np.int32(updated_position[0])
        self.y_position = np.int32(updated_position[1])
        self.z_position = np.int32(updated_position[2])

    def get_current_position(self):
        """
        Returns the current position of a satellite

        Returns
        -------
        x_position: int
        y_position: int
        z_position: int


        """
        return self.x_position, self.y_position, self.z_position
