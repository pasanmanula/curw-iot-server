## Bulk Update Data Format

This is adapted from [PWS - Upload Protocol](http://wiki.wunderground.com/index.php/PWS_-_Upload_Protocol#GET_parameters).
In order to upload data with multiple sampling.

### URL
<HOST_IP:PORT>/weatherstation/updateweatherstation

### Request Header
```bash
Content-Type: application/json
```

### Request Method
*POST*

### Request Body

```json
{
    "ID": "",
    "PASSWORD": "",
    "data": [{
        "dateutc": "YYYY-MM-DD HH:MM:SS",
        "rainin": "",
        "rainMM": "",
        "dailyrainin": "",
        "dailyrainMM": "",
        "rain": {"durationSec": 16, "durationMin": 5, "rainin": "", "rainMM": ""},
        
        "tempf": "",
        "tempc": "",
        
        "winddir": "",
        "windspeedmph": ""
    }],
    "health": {
        "batt": ""
    },
    "action": "updateraw",
    "softwaretype": "iCon"
}
```

#### List of Metadata fields

- ID [ID as registered to CUrW]
- PASSWORD [Station Key registered with this PWS ID, case sensitive]
- action [action=updateraw] -- always supply this parameter to indicate you are making a weather observation upload
- softwaretype - [text] ie: WeatherLink, VWS, WeatherDisplay, iCon

#### List of `data` filed object fields

- dateutc - [YYYY-MM-DD HH:MM:SS (mysql format)] In Universal Coordinated Time (UTC) Not local time

- tempf - [F outdoor temperature]
- tempc - [C outdoor temperature]

- rainin - [rain inches over the past hour)] -- the accumulated rainfall in the past 60 min
- dailyrainin - [rain inches so far today in local time]
- rainMM - [rain millimeters over the past hour)] -- the accumulated rainfall in the past 60 min
- dailyrainMM - [rain millimeters so far today in local time]

- winddir - [0-360 instantaneous wind direction]
- windspeedmph - [mph instantaneous wind speed]
- windgustmph - [mph current wind gust, using software specific time period]
- windgustdir - [0-360 using software specific time period]
- windspdmph_avg2m  - [mph 2 minute average wind speed mph]
- winddir_avg2m - [0-360 2 minute average wind direction]
- windgustmph_10m - [mph past 10 minutes wind gust mph ]
- windgustdir_10m - [0-360 past 10 minutes wind gust direction]

