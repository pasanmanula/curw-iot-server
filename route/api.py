from flask import Blueprint, request, jsonify
import app
import copy
from datetime import datetime

output_api = Blueprint('output_api', __name__)


@output_api.route('/weatherstation/<station_id>', methods=['GET'])
def get_weather_station_data(station_id):
    try:
        query = request.args.to_dict()
        app.logger_api.info("Request (API):: %s", query)
        start_date_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        end_date_time = datetime.now()
        if not isinstance(query, dict):
            raise Exception("Invalid request. Abort ...")
        else:
            try:
                if 'startDate' in query:
                    start_date_time = datetime.strptime(query['startDate'], '%Y-%m-%d')
                if 'endDate' in query:
                    end_date_time = datetime.strptime(query['endDate'], '%Y-%m-%d')

                if 'startDateTime' in query:
                    start_date_time = datetime.strptime(query['startDateTime'], '%Y-%m-%dT%H:%M:%S')
                if 'endDateTime' in query:
                    end_date_time = datetime.strptime(query['endDateTime'], '%Y-%m-%dT%H:%M:%S')
            except Exception as datetime_error:
                app.logger_api.error(datetime_error)
                return "Bad Request", 400
    except Exception as json_error:
        app.logger_api.error(json_error)
        return "Bad Request", 400

    station = app.wu_stations_map.get(station_id, None)
    if station is None:
        station = app.stations_map.get(station_id, None)

    if station is not None:
        app.logger_api.info("Station:: %s", station)
        meta_data = {
            'station': 'Hanwella',
            'type': 'Observed',
            'source': 'WeatherStation',
            'name': 'WUnderground',
        }
        meta_query = copy.deepcopy(meta_data)
        meta_query['station'] = station['name']
        meta_query['type'] = station['type']
        meta_query['source'] = station['source']
        meta_query['name'] = station['run_name']

        query_opts = {
            'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
            'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        timeseries = app.db_adapter.retrieve_timeseries(meta_query, query_opts)
        formatted_timeseries = []
        for s in timeseries:
            new_s = []
            for t in s['timeseries']:
                new_s.append([t[0].strftime('%Y-%m-%d %H:%M:%S'), float(t[1])])
            s['timeseries'] = new_s
            formatted_timeseries.append(s)
        print(formatted_timeseries)

        return jsonify(formatted_timeseries), 200
    else:
        app.logger_api.warning("Unknown Station: %s", station_id)
        return "Failure", 404
