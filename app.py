#!/usr/local/bin/python3

import os
import json
import logging
import copy
from logging.config import dictConfig
from os.path import join as pjoin
from datetime import datetime
from flask import Flask, request
from curwmysqladapter import MySQLAdapter, Station
from utils.UtilStation import get_station_hash_map
from utils import UtilValidation, UtilTimeseries
from config import Constants

app = Flask(__name__)

try:
    root_dir = os.path.dirname(os.path.realpath(__file__))
    config = json.loads(open(pjoin(root_dir, './config/CONFIG.json')).read())

    # Initialize Logger
    logging_config = json.loads(open(pjoin(root_dir, './config/LOGGING_CONFIG.json')).read())
    dictConfig(logging_config)
    logger = logging.getLogger('IoTServer')
    logger.addHandler(logging.StreamHandler())

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_DB = "curw"
    MYSQL_PASSWORD = ""

    if 'MYSQL_HOST' in config:
        MYSQL_HOST = config['MYSQL_HOST']
    if 'MYSQL_USER' in config:
        MYSQL_USER = config['MYSQL_USER']
    if 'MYSQL_DB' in config:
        MYSQL_DB = config['MYSQL_DB']
    if 'MYSQL_PASSWORD' in config:
        MYSQL_PASSWORD = config['MYSQL_PASSWORD']

    db_adapter = MySQLAdapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
    # Get Station Data for Bulk Data Format
    STATION_CONFIG = pjoin(root_dir, './config/StationConfig.json')
    CON_DATA = json.loads(open(STATION_CONFIG).read())
    stations_map = get_station_hash_map(CON_DATA['stations'])

    # Get Station Data for Single Upload Chinese weather stations
    STATION_CONFIG_WU = pjoin(root_dir, './config/StationConfigWU.json')
    CON_WU_DATA = json.loads(open(STATION_CONFIG_WU).read())
    wu_stations_map = get_station_hash_map(CON_WU_DATA['stations'])

    # Create common format with None values
    script_path = os.path.dirname(os.path.realpath(__file__))
    common_format = json.loads(open(os.path.join(script_path, './config/TimeStep.json')).read())
    for key in common_format:
        common_format[key] = None

except Exception as e:
    logging.error(e)


@app.route('/weatherstation/updateweatherstation', methods=['POST'])
def update_weather_station():
    try:
        content = request.get_json(silent=True)
        logger.info("Data:: %s", content)
        if not isinstance(content, object) and not content:
            raise Exception("Invalid request. Abort ...")
    except Exception as json_error:
        logger.error(json_error)
        return "Bad Request", 400

    station = stations_map.get(content.get('ID'), None)
    if station is not None:
        data = content['data']
        if len(data) < 1:
            logger.error("Request does not have data")
            return "Failure", 404
        timeseries = []

        is_precip_in_mm = True if 'rainMM' in data[0] else False
        pre_precip_mm = float(data[0]['rainMM']) if is_precip_in_mm else float(data[0]['rainin']) * 25.4
        for time_step in data:
            sl_time = datetime.strptime(time_step['dateutc'], Constants.DATE_TIME_FORMAT) + Constants.SL_OFFSET
            # Mapping Response to common format
            new_time_step = copy.deepcopy(common_format)

            # -- DateUTC
            if 'dateutc' in time_step:
                new_time_step['DateUTC'] = time_step['dateutc']
            # -- Time
            new_time_step['Time'] = sl_time.strftime(Constants.DATE_TIME_FORMAT)

            # -- TemperatureC
            if 'tempc' in time_step:
                new_time_step['TemperatureC'] = float(time_step['tempc'])
            # -- TemperatureF
            if 'tempf' in time_step:
                new_time_step['TemperatureC'] = (float(time_step['tempf']) - 32) * 5 / 9

            # -- PrecipitationMM
            new_time_step['PrecipitationMM'] = float(time_step['rainMM']) - pre_precip_mm \
                if is_precip_in_mm else float(time_step['rainin']) * 25.4 - pre_precip_mm
            pre_precip_mm = new_time_step['PrecipitationMM']

            timeseries.append(new_time_step)

        save_timeseries(db_adapter, station, timeseries)
        return "Success"
    else:
        logger.warning("Unknown Station: %s", station)
        return "Failure", 404


@app.route('/weatherstation/updateweatherstation.php', methods=['GET'])
def update_weather_station_single():
    try:
        data = request.args.to_dict()
        logger.info("Data:: %s", data)
        if not isinstance(data, dict) and not data:
            raise Exception("Invalid request. Abort ...")
    except Exception as json_error:
        logger.error(json_error)
        return "Bad Request", 400

    station = wu_stations_map.get(data.get('ID'), None)
    if station is not None:
        sl_time = datetime.strptime(data['dateutc'], Constants.DATE_TIME_FORMAT) + Constants.SL_OFFSET
        # Mapping Response to common format
        new_time_step = copy.deepcopy(common_format)

        is_precip_in_mm = True if 'rainMM' in data else False

        # -- DateUTC
        if 'dateutc' in data:
            new_time_step['DateUTC'] = data['dateutc']
        # -- Time
        new_time_step['Time'] = sl_time.strftime(Constants.DATE_TIME_FORMAT)

        # -- TemperatureC
        if 'tempc' in data:
            new_time_step['TemperatureC'] = float(data['tempc'])
        # -- TemperatureF
        if 'tempf' in data:
            new_time_step['TemperatureC'] = (float(data['tempf']) - 32) * 5 / 9

        # -- PrecipitationMM
        new_time_step['PrecipitationMM'] = float(data['rainMM']) \
            if is_precip_in_mm else float(data['rainin']) * 25.4

        save_timeseries(db_adapter, station, [new_time_step])
        return "Success"
    else:
        logger.warning("Unknown Station: %s", station)
        return "Failure", 404


def save_timeseries(adapter, station, timeseries):
    force_insert = True
    meta_data = {
        'station': 'Hanwella',
        'variable': 'Precipitation',
        'unit': 'mm',
        'type': 'Observed',
        'source': 'WeatherStation',
        'name': 'WUnderground',
    }

    logger.info('\n**************** STATION **************')
    logger.info('station name: %s, run_name: %s', station['name'], station['run_name'])
    #  Check whether station exists
    is_station_exists = adapter.get_station({'name': station['name']})
    if is_station_exists is None:
        logger.warning('Station %s does not exists.', station['name'])
        if 'station_meta' in station:
            station_meta = station['station_meta']
            station_meta.insert(0, Station.CUrW)
            row_count = adapter.create_station(station_meta)
            if row_count > 0:
                logger.warning('Created new station %s', station_meta)
            else:
                logger.error("Unable to create station %s", station_meta)
                return
        else:
            logger.error("Could not find station meta data to create new ", station['name'])
            return

    if len(timeseries) < 1:
        logger.error('INFO: Timeseries does not have any data : %s', timeseries)
        return

    logger.info('Start Date : %s', timeseries[0]['Time'])
    logger.info('End Date : %s', timeseries[-1]['Time'])
    start_date_time = datetime.strptime(timeseries[0]['Time'], '%Y-%m-%d %H:%M:%S')
    end_date_time = datetime.strptime(timeseries[-1]['Time'], '%Y-%m-%d %H:%M:%S')

    meta = copy.deepcopy(meta_data)
    meta['station'] = station['name']
    meta['start_date'] = start_date_time.strftime("%Y-%m-%d %H:%M:%S")
    meta['end_date'] = end_date_time.strftime("%Y-%m-%d %H:%M:%S")

    variables = station['variables']
    units = station['units']
    if 'run_name' in station:
        meta['name'] = station['run_name']
    for i in range(0, len(variables)):
        extracted_timeseries = UtilTimeseries.extract_single_variable_timeseries(timeseries, variables[i])
        if len(extracted_timeseries) < 1:
            logger.warning('Timeseries of variable:%s does not have data. Skip ...', variables[i])
            continue

        meta['variable'] = variables[i]
        meta['unit'] = units[i]
        event_id = adapter.get_event_id(meta)
        if event_id is None:
            event_id = adapter.create_event_id(meta)
            logger.info('HASH SHA256 created: %s', event_id)
        else:
            logger.info('HASH SHA256 exists: %s', event_id)
            meta_query = copy.deepcopy(meta_data)
            meta_query['station'] = station['name']
            meta_query['variable'] = variables[i]
            meta_query['unit'] = units[i]
            if 'run_name' in station:
                meta_query['name'] = station['run_name']
            query_opts = {
                'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            existing_timeseries = adapter.retrieve_timeseries(meta_query, query_opts)
            if len(existing_timeseries[0]['timeseries']) > 0 and not force_insert:
                logger.warning('Timeseries already exists. Use force insert to insert data.\n')
                continue

        validation_obj = {
            'max_value': station['max_values'][i],
            'min_value': station['min_values'][i],
        }
        extracted_timeseries = UtilValidation.handle_duplicate_values(extracted_timeseries, validation_obj)

        for l in extracted_timeseries[:3] + extracted_timeseries[-2:]:
            logger.debug(l)

        row_count = adapter.insert_timeseries(event_id, extracted_timeseries, force_insert)
        logger.info('%s rows inserted.\n' % row_count)


@app.route('/')
def index():
    return "Welcome to CUrW !"


if __name__ == '__main__':
    app.run(debug=True)
