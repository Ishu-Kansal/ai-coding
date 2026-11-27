from collections import defaultdict


class Leaderboard(object):
    
    def __init__(self, races):
        """Store the races whose results will be aggregated."""
        self.races = races

    def driver_points(self):
        """Aggregate each driver's points across every race and return totals keyed by display name."""
        driver_points = defaultdict(int)
        for race in self.races:
            for driver in race.results:
                name = race.driver_name(driver)
                driver_points[name] += race.points(driver)
        return driver_points

    def driver_rankings(self):
        """Return driver display names ordered by descending total points."""
        rankings = sorted(self.driver_points().items(), key=lambda x: x[1], reverse=True)
        return [name for (name, points) in rankings]


class Driver(object):
    def __init__(self, name, country):
        """Store a driver's name and country."""
        self.name = name
        self.country = country

class SelfDrivingCar(Driver):
    def __init__(self, algorithm_version, company):
        """Create a driverless-car entry with no human name and a company as its country."""
        Driver.__init__(self, None, company)
        self.algorithm_version = algorithm_version
        
class Race(object):

    _points = [25, 18, 15]

    def __init__(self, name, results):
        """Store the race name and finishing order, plus display names for regular and self-driving drivers."""
        self.name = name
        self.results = results
        self.driver_names = {}
        for driver in results:
            name = driver.name
            if isinstance(driver, SelfDrivingCar):
                name = "Self Driving Car - {} ({})".format(driver.country, driver.algorithm_version)
            self.driver_names[driver] = name

    def points(self, driver):
        """Return 25 points for first place, 18 for second, or 15 for third."""
        return Race._points[self.results.index(driver)]

    def driver_name(self, driver):
        """Return the driver's display name, including company and algorithm for self-driving cars."""
        return self.driver_names[driver]
