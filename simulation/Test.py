from PyAstronomy import pyasl
import math

EARTH_RADIUS = 6371000
# Orbit Altitude (Km)
ALTITUDE = 550
semiMajorAxis=float(ALTITUDE)*1000 + EARTH_RADIUS
STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14


def calculate_orbit_period(semi_major_axis=0.0):
    """ calculates the period of a orbit for Earth

    Parameters
    ----------
    semi_major_axis : float
        semi major axis of the orbit in meters

    Returns
    -------
    Period : int
        the period of the orbit in seconds (rounded to whole seconds)
    """

    tmp = math.pow(semi_major_axis, 3) / STD_GRAVITATIONAL_PARAMETER_EARTH
    return int(2.0 * math.pi * math.sqrt(tmp))


def initialize_position(planes, nodes_per_plane):
    # Abstände der Satelliten zueinander, bzw. im 360° wo befinden sich die Satelliten beim Start
    raan_offsets = [(360 / planes) * i for i in
                    range(0, planes)]

    # for xyzPos, auf welcher Zeitachse befindet sich der Satellit beim Start, wie raan_offsets aber als Zeitachse
    time_offsets = [(period / nodes_per_plane) * i for i in
                    range(0, nodes_per_plane)]

    # KeplerEllipse für eine einzige Ellipse
    # Bei mehr Ellipsen müsste man Omega auf die einzlnen raan_offsets mit einer for schleife erstellen
    ellipse = pyasl.KeplerEllipse(
        per=period,  # how long the orbit takes in seconds
        a=semiMajorAxis,  # if circular orbit, this is same as radius
        e=0,  # generally close to 0 for leo constillations
        Omega=raan_offsets[0],  # right ascention of the ascending node
        w=0.0,  # initial time offset / mean anamoly
        i=53)

    # increment ist dafür da, dass Satelliten nicht zusammenstoßen
    phase_offset = 0
    phase_offset_increment = ((period / nodes_per_plane) /
                              planes)
    temp = []
    toggle = False
    # this loop results puts thing in an array in this order:
    # [...8,6,4,2,0,1,3,5,7...]
    # so that the offsets in adjacent planes are similar
    # basically do not want the max and min offset in two adjcent planes
    for i in range(planes):
        if toggle:
            temp.append(phase_offset)
            print(temp, i)
        else:
            temp.insert(0, phase_offset)
            print(temp, i)
            # temp.append(phase_offset)
        toggle = not toggle
        phase_offset = phase_offset + phase_offset_increment

    phase_offsets = temp

    for plane in range(0, planes):
        for node in range(0, nodes_per_plane):
            # calculate the KE solver time offset
            offset = (time_offsets[node] + phase_offsets[plane])
            print(offset)
            init_pos = ellipse.xyzPos(offset)
            print(init_pos)


if __name__ == "__main__":
    period = calculate_orbit_period(semi_major_axis=semiMajorAxis)
    number_of_planes = 1
    nodes_per_plane = 1

    initialize_position(number_of_planes, nodes_per_plane)


