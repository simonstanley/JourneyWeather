class Traveller(object):
    """
    Class for tracking travel parameters. Adding distance or duration increases
    the other reletive to the current speed.
    All travel is forwards, there is no concept of location or direction so
    negative values for distance or duration are not allowed.
    Currently no units are assummed.

    """
    def __init__(self, distance=0., duration=0., speed=1.):
        self.distance = distance
        self.duration = duration
        self.speed    = speed

    def travel_distance(self, distance):
        """
        Negative values can be given, but duration is always incresed.

        """
        if distance < 0.:
            raise UserWarning("Can not travel backwards.")
        distance = float(distance)
        duration_travelled = distance / self.speed
        self.distance += distance
        self.duration += duration_travelled

    def travel_duration(self, duration):
        """
        Negative values can not be given.

        """
        if duration < 0.:
            raise UserWarning("Can not travel backwards in time.")
        duration = float(duration)
        distance_travelled = duration * self.speed
        self.distance += distance_travelled
        self.duration += duration
