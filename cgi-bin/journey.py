import coordinates
import step
from travel import Traveller

class Journey(object):
    """
    Class for a journey made up of a series of straight line steps (in the 
    given order).
    Main concept is to be able to travel the journey, currently it can only
    be travelled in one direction, from origin to destination.

    Args:

    * steps: list of Step instances.
        Must be given in order, steps must join i.e. each step destination
        must equal the next step's origin.

    """
    def __init__(self, steps):
        self.steps = self._check_steps(steps)

        # Extract data from steps.
        distance    = 0.
        coordinates = [self.steps[0].origin]

        for i, step in enumerate(self.steps):
            # Set numbered step attributes, starting at 0.
            setattr(self, "step%s" % i, step)
            distance += step.distance
            coordinates.append(step.destination)

        self.distance    = distance
        self.coordinates = coordinates
        self.origin      = self.coordinates[0]
        self.destination = self.coordinates[-1]

        # Create a concept of travel along the journey. Set to start of
        # journey.
        self.travel_reset()

    def __setattr__(self, name, value):
        if name == "current_step_indx" and hasattr(self, "current_step_indx"):
            # If not initialising current_step_indx, i.e. changing it,
            # update the current step
            self.current_step = self.steps[value]

        super(Journey, self).__setattr__(name, value)

    def _check_steps(self, steps):
        """
        Chech each step is valid and they all join to create a single journey.

        """
        for i, this_step in enumerate(steps):
            if type(this_step) != step.Step:
                raise UserWarning("Given steps are not all step.Step "\
                                  "instances.")
            if i > 0:
                if steps[i-1].destination != steps[i].origin:
                    raise UserWarning("Steps do not join.")

        return steps

    def _update_travel_log(self, dist, dur, spd):
        """
        To do

        """
        pass

    def travel_distance(self, distance, speed=None):
        """
        Travel along journey a given distance. Note, default is to use
        the speeds associates with each step. However, if a speed is provided
        this will be used instead.

        The various distance parameters:

        traveller.distance - How far we have travelled (in this travel)
        distance           - Total distance to be travelled
        dist_to_end        - How far is left to travel
        dist_to_step_end   - How far to the end on this step.

        """
        using_step_speeds = False
        if speed is None:
            # Set speed to current step speed.
            speed = self.current_step.speed
            using_step_speeds = True

        # Initialise traveller object, this tracks distance and duration
        # parameters.
        traveller = Traveller(distance=0., duration=0., speed=speed)

        while traveller.distance < distance:

            dist_to_end      = distance - traveller.distance
            dist_to_step_end = self.location.distance_to(
                               self.current_step.destination)

            if dist_to_end < dist_to_step_end:
                # The required distance to travel lies on the line of the
                # current step.
                traveller.travel_distance(dist_to_end)
                self.location = self.location.coord_calculater(
                                self.current_step.radians,
                                dist_to_end)

            elif dist_to_end >= dist_to_step_end:
                # Move to end of step and adjust parameters accordingly.
                traveller.travel_distance(dist_to_step_end)
                self.location = self.current_step.destination

                # Check if the journey has finished.
                if self.current_step_indx < len(self.steps) - 1:
                    # Not on the last step.
                    self.current_step_indx += 1
                    if using_step_speeds:
                        # Update speed to next step speed.
                        traveller.speed = self.current_step.speed
                else:
                    # Here we are at the journey's destination.
                    # If the given distance was larger then there is distance
                    # left in the journey, the while loop will continue because
                    # traveller.distance can not be larger then the journey's
                    # total distance. So reset it to 0 to stop this.
                    distance = 0.
                    print "Journey complete"


        self.distance_travelled += traveller.distance
        self.duration_travelled += traveller.duration

    def travel_duration(self, duration, speed=None):
        """

        """
        using_step_speeds = False
        if speed is None:
            # Set speed to current step speed.
            speed = self.current_step.speed
            using_step_speeds = True

        # Initialise traveller object, this tracks distance and duration
        # parameters.
        traveller = Traveller(distance=0., duration=0., speed=speed)

        while traveller.duration < duration:

            time_to_end      = duration - traveller.duration
            dist_to_step_end = self.location.distance_to(
                               self.current_step.destination)
            time_to_step_end = dist_to_step_end / traveller.speed

            if time_to_end < time_to_step_end:
                # The required duration to travel lands us on the line of the
                # current step.
                traveller.travel_duration(time_to_end)

                dist_to_end   = time_to_end * traveller.speed
                self.location = self.location.coord_calculater(
                                self.current_step.radians,
                                dist_to_end)

            elif time_to_end >= time_to_step_end:
                # Move to end of step and adjust parameters accordingly.
                traveller.travel_duration(time_to_step_end)
                self.location = self.current_step.destination

                # Check if the journey has finished.
                if self.current_step_indx < len(self.steps) - 1:
                    # Not on the last step.
                    self.current_step_indx += 1
                    if using_step_speeds:
                        # Update speed to next step speed.
                        traveller.speed = self.current_step.speed
                else:
                    duration = 0.
                    print "Journey complete"

        self.distance_travelled += traveller.distance
        self.duration_travelled += traveller.duration

    def travel_reset(self):
        """
        Set/reset all travel attributes to start.

        """
        self.location = self.origin
        self.current_step_indx  = 0
        self.current_step       = self.steps[0]
        self.distance_travelled = 0.
        self.duration_travelled = 0.
        self.travel_log = {}

    def summary(self):
        """
        Print a summary of the journey and the current travel along it.

        """
        print "Journey Summary:\n"
        print "Route"
        print "\tOrigin:\t\t\t %s" % self.origin
        print "\tDestination:\t\t %s" % self.destination
        print "\tJourney coordinates:\t %s" % self.coordinates
        print "\tTotal distance:\t\t %s" % self.distance
        print
        print "Travel"
        print "\tCurrent location:\t %s" % self.location
        print "\tCurrent step:\t\t %s" % self.current_step
        print "\tDistance travelled:\t %s" % self.distance_travelled
        print "\tDuration travelled:\t %s" % self.duration_travelled
