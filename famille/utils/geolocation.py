from math import acos, cos, sin, radians

from pygeocoder import Geocoder


EARTH_RADIUS =  6371009.0


def geolocate(address):
    """
    Geolocate an address, i.e. return its
    GPS coordinates.

    :param address:         the address to geolocalize
    """
    return Geocoder.geocode(address)[0].coordinates


def geodistance(origin, to):
    """
    Calculate the distance from a GPS point to another,
    using the spherical law of cosines.
    See http://www.movable-type.co.uk/scripts/latlong.html

    :param origin:    a tuple of latitude, longitude
    :param to:        a tuple of latitude, longitude
    """
    lat1, lon1 = origin
    lat2, lon2 = to
    delta_lon = lon2 - lon1

    lat1, lat2, delta_lon = map(radians, (lat1, lat2, delta_lon))
    return acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(delta_lon)) * EARTH_RADIUS
