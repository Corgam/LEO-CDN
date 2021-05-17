from enum import Enum


class KeygroupAreas(Enum):
    NORTHWEST = 0
    SOUTHWEST = 1
    SOUTHEAST = 2
    NORTHEAST = 3


def keygroup_area_for_point(p, decision_planes):
    normal0, d0 = decision_planes[0]
    normal1, d1 = decision_planes[1]

    h0 = p @ normal0 - d0
    h1 = p @ normal1 - d1

    if h0 >= 0 and h1 >= 0:
        return KeygroupAreas.NORTHWEST
    elif h0 < 0 and h1 >= 0:
        return KeygroupAreas.SOUTHWEST
    elif h0 >= 0 and h1 < 0:
        return KeygroupAreas.SOUTHEAST
    else:
        return KeygroupAreas.NORTHEAST


def define_decision_planes(ellipse):
    center = ellipse.xyzCenter()
    p0 = ellipse.xyzPos(0)
    normal0 = p0 - center
    d0 = -(normal0 @ center)

    p1 = ellipse.xyzPos(ellipse.per / 4)
    normal1 = p1 - center
    d1 = -(normal1 @ center)

    return (normal0, d0), (normal1, d1)
