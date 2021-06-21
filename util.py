import math
import numpy as np

# TODO: refactor to use the function from coordinator
# Currently can't import due to import error in satellite

EARTH_RADIUS = 6371000  # in meter
ALTITUDE = 550  # Orbit Altitude (Km)

# according to wikipedia
STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14
# seconds the earth needs to make one whole rotation
SECONDS_PER_DAY = 60 * 60 * 24
# earth's z axis (eg a vector in the positive z direction)
EARTH_ROTATION_AXIS = [
    0,
    0,
    1,
]  # this means the north pole is on the top and the south pole is on the bottom
SEMI_MAJOR_AXIS = float(ALTITUDE) * 1000 + EARTH_RADIUS


def transform_geo_to_xyz(lat, lon):
    """
    Transforms any latitude and longitude to xyz coordinates.
    Taken from Ben S. Kempton.
    Parameters
    ----------
    lat
    lon

    Returns
    -------

    """
    # must convert the lat/long/alt to cartesian coordinates
    radius = EARTH_RADIUS + ALTITUDE
    init_pos = [0, 0, 0]
    latitude = math.radians(lat)
    longitude = math.radians(lon)
    init_pos[0] = radius * math.cos(latitude) * math.cos(longitude)  # x
    init_pos[1] = radius * math.cos(latitude) * math.sin(longitude)  # y
    init_pos[2] = radius * math.sin(latitude)  # z

    pos = init_pos

    x = np.int32(pos[0])
    y = np.int32(pos[1])
    z = np.int32(pos[2])

    return x, y, z
