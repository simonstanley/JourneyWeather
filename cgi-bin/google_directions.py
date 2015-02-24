#!/usr/bin/env python
import cgi
import cgitb
import requests
import datapoint
import datetime
import dateutil.parser
import math
import json
from coordinates import Coordinate
from step import Step
from journey import Journey

google_dir_url = "http://maps.googleapis.com/maps/api/directions/json?"\
                 "origin={olat},{olon}&destination={dlat},{dlon}{opts}"
API_key = "f8fbd9db-0b2d-45f2-9e7b-92f35fe42279"
DATE_FORMAT = "%Y-%m-%dZ"

def print_response(response):
    """

    """
    print "Content-Type: text/html"
    print
    print response

def convert_json_to_dict(str_json):
    """

    """
    try:
        data_dict = json.loads(str_json)
    except ValueError:
        raise ValueError("Invaild JSON format.")
    return data_dict

def convert_dict_to_json(dictionary):
    """

    """
    return json.dumps(dictionary, sort_keys=True, indent=4, 
                      separators=(',', ': '))

def iso2datetime(iso_time):
    """

    """
    return dateutil.parser.parse(iso_time)

def sort_time(time):
    """

    """
    if time is None:
        time = datetime.datetime.now()
    else:
        time = iso2datetime(time)
    return time

def get_journey(directions_json):
    """
    Check the returned directions JSON is valid for these purposes and extract
    the journey data.

    """
    if directions_json['status'] == "ZERO_RESULTS":
        raise UserWarning("Direction for these coordinates have not been found")

    # We only request one route at a time.
    if len(directions_json['routes']) > 1:
        raise UserWarning("Multiple routes have been loaded. Can't handle "\
                          "this!")
    route = directions_json['routes'][0]

    # We only request one leg at a time.
    if len(route['legs']) > 1:
        raise UserWarning("Multiple legs have been loaded. Can't handle this!")

    return route['legs'][0]

def get_coord_from_step(step, location):
    """
    Get coordinates from journey step and convert to Coordninate instances.

    """
    return Coordinate(step[location]['lng'],
                      step[location]['lat'],
                      coord_type="geographic",
                      strict=True)

def create_steps(journey_dict):
    """
    Extract the coordinates of each step in the journey.

    """
    steps = []
    for step in journey_dict['steps']:
        origin      = get_coord_from_step(step, 'start_location')
        destination = get_coord_from_step(step, 'end_location')
        duration    = step['duration']['value']
        steps.append(Step(origin, destination, duration=duration))
    return steps

def create_forecast_dict(longitude, latitude, forecast, time):
    """

    """
    return {"location" : {"lon" : longitude,
                          "lat" : latitude},
            "forecast" : forecast,
            "time"     : time}

def get_forecast(conn, site, dtime):
    """

    """
    forecast = conn.get_forecast_for_site(site.id, "3hourly")

    # Each forecast instance includes all forecasts for the next 5 days.
    # Here we establish which forecast matches the given time.
    first_forecast_dtime = datetime.datetime.strptime(forecast.days[0].date,
                                                      DATE_FORMAT)
    secs_diff = (dtime - first_forecast_dtime).total_seconds()

    # We need this in turns of days and minutes in order to make compatable
    # with datapoint metadata
    days_diff = int(math.floor(secs_diff / (24 * 60 * 60)))
    # Forecasts only exist for the next 5 days.
    if days_diff <= 5:
        mins_diff = (secs_diff / 60) - (days_diff * (24 * 60))
        # Forecasts are 3 hourly (180 minutes). Find nearest forecast time
        required_timestep = int(round(mins_diff / 180., 0) * 180.)
        for timestep in forecast.days[days_diff].timesteps:
            if timestep.name == required_timestep:
                return timestep.weather.text
    else:
        raise UserWarning("The forecast period does not extend to the whole "\
                          "time of your journey.")

def main(request_dict):
    """

    """
    origin      = request_dict['origin']
    destination = request_dict['destination']
    options     = request_dict['options']
    fcst_points = request_dict['fcst_points']
    start_time  = sort_time(request_dict['start_time'])

    google_req_url = google_dir_url.format(olat=origin["latitude"],
                                           olon=origin["longitude"],
                                           dlat=destination["latitude"],
                                           dlon=destination["longitude"],
                                           opts=options)
    directions_request = requests.get(google_req_url)
    directions_json    = directions_request.json()

    # The directions_json is structured to hold multiple sets of directions for
    # multiple routes and legs. This module will only handle one route with one
    # leg. Check this and extract this leg, and call it the journey.
    journey_dict  = get_journey(directions_json)
    journey_steps = create_steps(journey_dict)
    journey       = Journey(journey_steps)

    # According to how many forecast points along the journey are required,
    # work out the distance between each point.
    travel_dist = journey.distance / (fcst_points - 1)

    # Open up datapoint connection
    conn = datapoint.connection(api_key=API_key)

    start_site = conn.get_nearest_site(journey.location.x,
                                       journey.location.y)
    start_forecast = get_forecast(conn, start_site, start_time)
    print start_time.isoformat()
    forecasts = [create_forecast_dict(start_site.longitude,
                                      start_site.latitude,
                                      start_forecast,
                                      start_time.isoformat())]

    while journey.location != journey.destination:
        journey.travel_distance(travel_dist)
        time = start_time + \
               datetime.timedelta(seconds=journey.duration_travelled)
        site = conn.get_nearest_site(journey.location.x,
                                     journey.location.y)
        forecast = get_forecast(conn, site, time)
        forecasts.append(create_forecast_dict(site.longitude,
                                              site.latitude,
                                              forecast,
                                              time.isoformat()))

    response_dict = convert_dict_to_json({"journey" : forecasts})
    print_response(response_dict)

    # for fcst in forecasts:
    #     print "location:\t", fcst["location"]
    #     print "time:\t\t", fcst["time"]
    #     print "Weather:\t", fcst["forecast"]
    #     print


if __name__ == "__main__":

    cgitb.enable()
    form = cgi.FieldStorage()
    str_json = form["query"].value

    # str_json = '{"origin":{"latitude":51.833,'\
    #                       '"longitude":-0.74},'\
    #             '"destination":{"latitude":54.2,'\
    #                            '"longitude":-2.3},'\
    #             '"options":"",'\
    #             '"fcst_points":7,'\
    #             '"start_time":null}'


    request_dict = convert_json_to_dict(str_json)
    main(request_dict)
