import datetime
from dataclasses import dataclass
from math import sin, cos, sqrt, atan2, radians

# approximate radius of earth in km
R = 6373.0
MINUTES_PER_HOUR = 60
SECONDS_PER_HOUR = 3600


# File responsibility: provides geographic calculations for the application.
# It converts latitude/longitude pairs into great-circle distances, estimates
# travel times using an average speed, and can update that speed from observed
# travel. It is the route/calculation boundary used by DeliveryController.

@dataclass
class Location:
    latitude: float
    longitude: float


class MapService:
    def __init__(self, average_speed=50):
        # Business logic: establishes the speed baseline used for ETA estimates.
        "average speed in km/h"
        self.average_speed = average_speed

    def calculate_eta(self, location1 : Location, location2 : Location) -> float:
        # Business logic: computes great-circle distance in kilometers and
        # converts travel time at the configured average speed to minutes.
        #
        # Formula truth:
        # | distance | average speed | ETA |
        # |----------|---------------|-----|
        # | 0 km     | >0 km/h       | 0 minutes |
        # | >0 km    | >0 km/h       | distance / speed * 60 minutes |
        "return the number of minutes it will take to travel between locations at average speed."
        distance = self.calculate_distance(location1, location2)
        return distance / self.average_speed * MINUTES_PER_HOUR

    def calculate_distance(self, location1 : Location, location2 : Location) -> float:
        # Business logic: calculates the shortest surface distance between two
        # latitude/longitude points using the Haversine formula and an approximate
        # Earth radius of 6373 km.
        #
        # Truth table:
        # | locations are identical | Haversine result |
        # |-------------------------|------------------|
        # | Yes                     | 0 km |
        # | No                      | Distance on Earth's surface in km |
        lat1 = radians(location1.latitude)
        lon1 = radians(location1.longitude)
        lat2 = radians(location2.latitude)
        lon2 = radians(location2.longitude)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        # km
        distance = R * c
        return distance

    def update_average_speed(self, location1 : Location, location2 : Location, elapsed_time: datetime.timedelta):
        # Business logic: derives an observed average speed from the distance
        # between two route points and elapsed travel time, then replaces the
        # service's ETA speed baseline with that result.
        #
        # Truth table:
        # | elapsed time | observed distance | average_speed |
        # |--------------|-------------------|---------------|
        # | >0 seconds   | Any               | distance / elapsed hours |
        # | <=0 seconds  | Any               | Raises ValueError |
        elapsed_seconds = elapsed_time.total_seconds()
        if elapsed_seconds <= 0:
            raise ValueError("elapsed_time must be greater than zero")

        distance = self.calculate_distance(location1, location2)
        updated_speed = distance / (elapsed_seconds / SECONDS_PER_HOUR)
        self.average_speed = updated_speed

