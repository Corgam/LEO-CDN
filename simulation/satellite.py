from PyAstronomy import pyasl


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
        current_position = self.kepler_ellipse.xyzPos(offset)
        self.x_position = current_position[0]
        self.y_position = current_position[1]
        self.z_position = current_position[2]

    def set_new_position(self, offset):
        """
        Sets the new position of a satellite.

        Parameters
        ----------
        offset

        Returns
        -------

        """
        updated_position = self.kepler_ellipse.xyzPos(offset)
        self.x_position = updated_position[0]
        self.y_position = updated_position[1]
        self.z_position = updated_position[2]

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

