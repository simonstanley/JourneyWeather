import math

def roll_coord(coord, coord_range):
    """
    Roll coord into given range, if outside.

    """
    min_val = min(coord_range)
    max_val = max(coord_range)
    roll_amount = max_val - min_val

    if coord <= min_val:
        while coord <= min_val:
            coord += roll_amount

    elif coord >= max_val:
        while coord >= max_val:
            coord -= roll_amount

    return coord

def distance(coord1, coord2):
    """
    Calculate distance between two coordinates.

    """
    x_length = coord2.x - coord1.x
    y_length = coord2.y - coord1.y
    # Pythagoras theorem
    return (x_length ** 2 + y_length ** 2) ** 0.5


class Coordinate(object):
    """
    Class for holding and performing calculations with 2D coordinates.

    Args:

    * x, y: integers or floats
        The two coordinate values

    Kwargs:

    * coord_type: None or string
        If None, values are taken as values with no special treatment.
        Available coordinate types:

            'geographic' - For latitude and longitude coordinates

    * strict: boolean
        If True (default) an error is raised if the given coordinates do not
        conform to the given coord_type. If False, the class will try to
        translate the given values into the corrd_type format.
        If coord_type is None, this has no effect.

    """
    def __init__(self, x, y, coord_type=None, strict=True):
        self.coord_type = coord_type
        self._strict = strict
        if self.coord_type:
            x, y = self._check_coords(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return "(%s, %s)" % (self.x, self.y)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if type(self) == type(other):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def _check_coords(self, x, y):
        coord_type_method = '_' + self.coord_type
        if hasattr(self, coord_type_method):
            x, y = getattr(self, coord_type_method)(x, y)
        else:
            raise UserWarning('Invalid coord type - %s.' % coord_type)

        return float(x), float(y)

    def _geographic(self, x, y):
        """
        Check x and y refer to valid latitude and longitude coordinates.
        If not strict, coords are adjusted to fall in the range x: -180 - 180,
        y: -90 - 90.

        """
        if self._strict:
            if not (-180. <= x <= 360.):
                raise UserWarning("Invalid latitude (x) coordinate %s." % x)

            if not (-90. <= y <= 90.):
                raise UserWarning("Invalid longitude (y) coordinate %s." % y)

        else:
            # Not being strict so adjust coords into desired range.
            x = roll_coord(x, [-180., 180.])
            y = roll_coord(y, [-90., 90.])

        return x, y

    def coord_calculater(self, radians, distance):
        """
        Return new coordinate for the point at the specified distance and angle
        from this coordinate. Angle must be given in radians.
        Distance is taken to be in the same units as the coordinate.

        """
        # Use trigonometry with distance being the hypotenuse. The adjacent refers
        # to the x direction and the opposite to the y direction.
        xtra_x = distance * math.cos(radians)
        xtra_y = distance * math.sin(radians)
        return Coordinate(self.x + xtra_x, self.y + xtra_y,
                          coord_type=self.coord_type, strict=self._strict)

    def distance_to(self, coord):
        """
        Give another Coordinate instance and return its distance from this
        coordinate.

        """
        x_length = coord.x - self.x
        y_length = coord.y - self.y
        # Pythagoras theorem
        return (x_length ** 2 + y_length ** 2) ** 0.5
