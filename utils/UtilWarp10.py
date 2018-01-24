from datetime import datetime
import requests
import pytz

from config import Constants

WARP10_CONFIGS = {
    'host': '10.128.0.2',
    'port': 8080,
    'class-name-prefix': 'curw.test.',
    'read-token': 'SRBXW1yUp5sJz4Czr0cn_Q4pXtkQtyfmOhqHuqlkZ.x8XA5OOE42NKw.bOd6xyXB4t3oQbijIIMimtlUhBWTd_zjGY6d2DWjlH_NqM5FY533w9cnCF7VrzE5LIcoSS8wBslClD0Vb1MXpvM4CN_PE1H41UGWy.HN',
    'write-token': '3tvXWXNHph_l8v1iTAblmdQOQ7IU_TGmkaprAmQTULNWCcC6f95XSzTwbp8UqtFZLCCHHgSnijrhBYfKWSFKzlwZgu_rwme_YodxLmv9uWvh7TkSAjgb6pIA7C_SxgUq',
    'token-header': 'X-Warp10-Token'
}

WARP10_UPDATE_ENDPOINT = 'http://%s:%d/api/v0/update' % (WARP10_CONFIGS['host'], WARP10_CONFIGS['port'])

# Sri-Lankan Timezone.
sl_timezone = pytz.timezone('Asia/Colombo')


def forward_to_warp10_platform(station, time_step):
    """
    Utility function to froward the station data to WARP10 Platform.
    :param station: staion['station_meta'] should be a list containing the followings,
    [0] - stationId
    [1] - name
    [2] - lattitude
    [3] - longitude
    :param time_step: time_step is dictionary of common format as defined config/TimeStep.json
    time_step dictionary can have keys with no or empty value.
    :return: Response
    """
    headers = {WARP10_CONFIGS['token-header']: WARP10_CONFIGS['write-token']}

    # Timestamp of the reading in microseconds since the Unix Epoch.
    timestamp_sec = datetime.strptime(time_step['DateUTC'], Constants.DATE_TIME_FORMAT).timestamp()
    timestamp = round(timestamp_sec * 1000000)

    data = ''
    for key, value in time_step.items():
        # Think of a way to store 'Ticks'.
        if key == 'Ticks' or key == 'DateUTC' or key == 'Time' or (not value):
            continue
        # TS/LAT:LON/ELEV
        lat = station['station_meta'][2]
        lon = station['station_meta'][3]
        data = data + str(timestamp) + '/' + str(lat) + ':' + str(lon) + '/'

        # Space separation
        data = data + ' '

        # NAME{LABELS}
        station_id = station['station_meta'][0]
        gts_class_name = WARP10_CONFIGS['class-name-prefix'] + str(key)
        labels = '{stationId=%s}' % station_id
        data = data + (gts_class_name + labels)

        # Space separation
        data = data + ' '

        # VALUE
        data = data + str(value)

        # Newline separation
        data = data + '\n'
    return requests.post(url=WARP10_UPDATE_ENDPOINT, headers=headers, data=data)


if __name__ == '__main__':
    timeStep = {
        'Time': datetime.now(),
        'TemperatureC': 60,
        'DailyPrecipitationMM': 60,
        'PrecipitationMM': 60,
        'Ticks': [23, 45, 34],
        'DewpointC': 60,
        'WindDirection': 60,
        'WindDirectionDegrees': 60,
        'WindSpeedKMH': 60,
        'WindSpeedGustKMH': 60,
        'Humidity': 60,
        'SolarRadiationW/m2': 60,
        'DateUTC': datetime.now(tz=pytz.utc)
    }

    stationData = {
        'station_meta': ['curw_hingurana', 'Hingurana', 6.904552, 80.407895, 0, 'Hingurana Station']
    }

    print(forward_to_warp10_platform(stationData, timeStep))
