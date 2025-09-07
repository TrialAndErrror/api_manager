from geopy import Nominatim


def get_longitude_and_latitude_for_address(address: str):
    geolocator = Nominatim(user_agent="api_manager_location")
    location = geolocator.geocode(query=address)

    if not location:
        raise Exception("Could not find coordinates for address")

    return location.latitude, location.longitude
