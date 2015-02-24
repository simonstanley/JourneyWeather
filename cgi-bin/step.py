import numpy
import math
import coordinates
from line import StraightLine

def straight_line_equation(x1, y1, x2, y2, give_direction=False):
    """
    Given two sets of coordinates, calculate the straight line which intersects
    them both. Returned values are A and B from the straight line equation
    y = Ax + B.

    Option to return the direction. '+' is returned if (x2, y2) is above or
    horizontally right of (x1, y1), and '-' if it is below or horizontally left.

    """
    if x1 == x2 and y1 == y2:
        raise UserWarning("Coordinates must differ.")

    # 'A' is the gradient, re-arrange y = Ax to get A = y/x.
    y = (y2 - y1)
    x = (x2 - x1)
    if x == 0:
        gradient = numpy.inf
    else:
        gradient = float(y) / float(x)

    # 'B' is the shift in the y direction. Assume it to be 0 and see the
    # difference from y1 when x = x1.
    y = gradient * x1
    shift = y1 - y

    if give_direction:
        if y2 > y1:
            direction = '+'
        elif y2 < y1:
            direction = '-'
        else: # y1 == y2, so look at x values.
            if x2 > x1:
                direction = '+'
            elif x2 < x1:
                direction = 'i'
        return gradient, shift, direction

    else:
        return gradient, shift

def gradient_to_radians(gradient, direction='+'):
    """
    To convert this properly we must translate the gradient into a vector, i.e.
    it needs a direction. If you picture a line running straight across an xy
    graph, it has no direction. Setting direction as '+' says the line is going
    up (or right if horizontal, i.e. gradient=0), and setting it to '-' says
    the line is going down (or left if horizontal).
    The returned value is radians from the x-axis to the line, going
    anti-clockwise.

    """
    radians = math.atan(gradient)
    if direction == '+':
        if radians < 0.:
            radians += math.pi

    elif direction == '-':
        if radians < 0.:
            radians += (2 * math.pi)
        else:
            radians += math.pi
    return radians


class Step(object):
    """
    Class for a step between two coordinates. No units are assumed.

    """
    def __init__(self, origin, destination, duration=None, speed=None):
        self.origin      = self._sort_coord(origin)
        self.destination = self._sort_coord(destination)
        gradient, shift, direction = straight_line_equation(self.origin.x,
                                                            self.origin.y,
                                                            self.destination.x,
                                                            self.destination.y,
                                                            give_direction=True)
        self.line_equation = StraightLine(gradient, shift)
        self.radians = gradient_to_radians(self.line_equation.gradient,
                                           direction)
        self.distance = self.origin.distance_to(self.destination)

        if duration is None and speed is None:
            self.duration = self.distance
            self.speed    = 1.

        elif duration is not None and speed is not None:
            if round(speed, 5) != round(self.distance / duration, 5):
                raise UserWarning("The given speed and duration do not match "\
                                  "the distance between the coordinates. "
                                  "Unfortunately, currently values for speed '\
                                  'and duration must be given in equivalent "\
                                  "units as the coordinates.")
            else:
                self.duartion = duration
                self.speed    = speed

        elif duration is not None:
            self.duration = duration
            self.speed    = self.distance / self.duration

        elif speed is not None:
            self.speed    = speed
            self.duration = self.distance / self.speed

    def __repr__(self):
        return "%s to %s" % (self.origin, self.destination)

    def __str__(self):
        return self.__repr__()

    def _sort_coord(self, coord):
        """
        Check given coords are valid, convert to Coordinate class instance
        if not already.

        """
        err_message = "Invalid coordinate given: %s"
        if type(coord) != coordinates.Coordinate:
            if type(coord) in [list, tuple]:
                if len(coord) == 2:
                    coord = coordinates.Coordinate(coord[0], coord[1])
                else:
                    raise UserWarning(err_message % coord)
            else:
                raise UserWarning(err_message % coord)
        return coord
