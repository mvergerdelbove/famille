import logging
from math import acos, cos, sin, radians
import traceback

from geopy import geocoders, exc as geopy_exc

from famille import errors


EARTH_RADIUS =  6371.0  # in km


geocoder = geocoders.GoogleV3(scheme="http")


def geolocate(address):
    """
    Geolocate an address, i.e. return its
    GPS coordinates.

    :param address:         the address to geolocalize
    """
    try:
        _, (lat, lon) = geocoder.geocode(address)
        return lat, lon
    except geopy_exc.GeopyError:
        logging.critical("Cannot geolocate address due to API error: %s", traceback.format_exc())
        raise errors.GeolocationError("Address '%s' cannot be geolocated" % address)


def geodistance(origin, to):
    """
    Calculate the distance from a GPS point to another,
    using the spherical law of cosines.
    See http://www.movable-type.co.uk/scripts/latlong.html

    :param origin:    a Geolocation model
    :param to:        a Geolocation model
    """
    lat1, lon1 = origin.lat, origin.lon
    lat2, lon2 = to.lat, to.lon
    delta_lon = lon2 - lon1

    lat1, lat2, delta_lon = map(radians, (lat1, lat2, delta_lon))
    return acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(delta_lon)) * EARTH_RADIUS


def is_close_enough(origin, to, distance):
    """
    A utility function that computes if a point is close
    enough to another point.

    :param origin:         a Geolocation model
    :param to:             a Geolocation model
    :param distance:       the distance to test
    """
    if not origin or not to:
        raise ValueError("One of the two points is missing")

    return geodistance(origin, to) <= distance
