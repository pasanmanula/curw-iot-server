import requests


def get_station_hash_map(stations):
    hash_map = {}
    for station in stations:
        if station.get('stationId', None) is not None:
            hash_map[station.get('stationId')] = station

    return hash_map


def forward_to_weather_underground(data, logger):
    r = requests.get('https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php', params=data)
    logger.info('WeatherUnderground >> %s, %s', r.status_code, r.text)


def forward_to_dialog_iot(data, logger):
    r = requests.get('https://h.a.ideabiz.lk/weatherstation/updateweatherstation.php', params=data)
    logger.info('Dialog IoT >> %s, %s', r.status_code, r.text)
