var startPos = null;
var endPos   = null;
WEATHER_CODES = {
	"Sleet shower (day)":"w17.gif",
	"Sleet shower (night)":"w16.gif",
	"Cloudy":"w7.gif",
	"Fog":"w6.gif",
	"Hail shower (night)":"w19.gif",
	"Hail":"w21.gif",
	"Light snow shower (night)":"w22.gif",
	"Thunder shower (day)":"w29.gif",
	"Sleet":"w18.gif",
	"Partly cloudy (day)":"w3.gif",
	"Heavy rain":"w15.gif",
	"Light rain shower (day)":"w10.gif",
	"Heavy snow shower (day)":"w26.gif",
	"Heavy snow":"w27.gif",
	"Mist":"w5.gif",
	"Clear night":"w0.gif",
	"Hail shower (day)":"w20.gif",
	"Light snow shower (day)":"w23.gif",
	"Light rain shower (night)":"w9.gif",
	"Overcast":"w8.gif",
	"Heavy rain shower (night)":"w13.gif",
	"Not used":"w4.gif",
	"Heavy rain shower (day)":"w14.gif",
	"Light rain":"w12.gif",
	"Heavy snow shower (night)":"w25.gif",
	"Thunder shower (night)":"w28.gif",
	"Light snow":"w24.gif",
	"Thunder":"w30.gif",
	"Sunny day":"w1.gif",
	"Partly cloudy (night)":"w2.gif",
	"Drizzle":"w11.gif"
}


$(document).ready(function(){

	function initialize() {
		var mapProp = {
	    	center:new google.maps.LatLng(54.6,-4.0),
	    	zoom:5,
	    	mapTypeId:google.maps.MapTypeId.ROADMAP
	  	};
	  	var map=new google.maps.Map(document.getElementById("map"),mapProp);

	  	// Listen for map clicks defining the journey start and end.
		google.maps.event.addListener(map, 'click', function(event) {
			set_journey(map, event.latLng);
		});

	}

	function set_journey(map, location) {
		if (startPos == null) {
			startPos = location;
			add_marker(map, location, "symbols/pin_blue.ico", "Start");
		}
		else if (endPos == null) {
			endPos = location;
			//add_marker(map, location, "symbols/pin_red.ico", null);
			var journey_json = create_journey();
			// Get weather forecasts for journey.
			$.post(
				'cgi-bin/google_directions.py',
				journey_json,
				function(data, status) {
					var journey_weather = JSON.parse(data);
					for (i in journey_weather.journey) {
						var journey = journey_weather.journey[i];
						var fcstPos = new google.maps.LatLng(journey.location.lat,
															 journey.location.lon)
						add_marker(map, fcstPos, "symbols/" + WEATHER_CODES[journey.forecast],
								   journey.time.substring(0, 10) + " " + journey.time.substring(11, 19))
					}
				});
		}
	}

	function add_marker(map, location, icon, title) {
		var marker=new google.maps.Marker({
			position: location,
			icon: icon,
			title: title
		});
		marker.setMap(map);
	}

	function create_journey() {
		var journey_json = {};
		journey_json.origin = {};
		journey_json.origin.latitude = startPos.lat();
		journey_json.origin.longitude = startPos.lng();
		journey_json.destination = {};
		journey_json.destination.latitude = endPos.lat();
		journey_json.destination.longitude = endPos.lng();

		// Extra arguments to be developed.
		journey_json.options = '';
		journey_json.fcst_points = 7;
		journey_json.start_time = null; // This results in using current time.

		// Return as query string.
		return "query=" + JSON.stringify(journey_json)
	}

	google.maps.event.addDomListener(window, 'load', initialize);

});