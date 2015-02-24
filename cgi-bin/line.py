class StraightLine(object):
    def __init__(self, gradient, shift):
        self.gradient = gradient
        self.shift    = shift

    def __call__(self, val):
        return (val * self.gradient) + self.shift

    def __repr__(self):
        rep_shift = abs(self.shift)
        if self.shift < 0:
            sign = '-'
        else:
            sign = '+'
        return "%sx %s %s" % (self.gradient, sign, rep_shift)

    def __str__(self):
        return self.__repr__()
