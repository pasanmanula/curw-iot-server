## Bulk Update Data Format

This protocol is adapted from [PWS - Upload Protocol](http://wiki.wunderground.com/index.php/PWS_-_Upload_Protocol#GET_parameters).
It is capable of upload data with multiple sampling.

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
        "rain": ["YYYY-MM-DD HH:MM:SS", "YYYY-MM-DD HH:MM:SS"],
        
        "tempf": "",
        "tempc": "",
        
        "winddir": "",
        "windspeedmph": ""
    }],
    "health": {
        "batt": ""
    },
    "action": "updateraw",
    "softwaretype": "iCon",
    "version": "1.3.6"
}
```

#### List of Metadata fields

- **ID** [ID as registered to CUrW]
- **PASSWORD** [Station Key registered with this PWS ID, case sensitive]
- **action** [action=updateraw] -- always supply this parameter to indicate you are making a weather observation upload
- **softwaretype** - [text] ie: WeatherLink, VWS, WeatherDisplay, iCon, Dialog
- **version** - [text] ie: 0.4.2, v1.7.2
- **data** [JSON Array of `data` Objects] - can contain multiple `data` object as described below

#### List of `data` filed object fields

`datautc` filed is *required* and other fields are *optional*.

Can send the details using appropriate fields.
Eg. if the station is measuring temperature in Fahrenheit, then the value can be send with `tempf` field (avoid sending `tempc`). 

- **dateutc** - [YYYY-MM-DD HH:MM:SS (mysql format) or UNIX Timestamp] In Universal Coordinated Time (UTC) Not local time

- **tempf** - [F outdoor temperature]
- **tempc** - [C outdoor temperature]

- **rainin** - [rain inches over the past hour)] -- the accumulated rainfall in the past 60 min
- **dailyrainin** - [rain inches so far today in local time]
- **rainMM** - [rain millimeters over the past hour)] -- the accumulated rainfall in the past 60 min
- **dailyrainMM** - [rain millimeters so far today in local time]

- **rain** - [List of Date Time value of each tick of Rain Gauge tipping bucket in YYYY-MM-DD HH:MM:SS or UNIX Timestamp]

- **winddir** - [0-360 instantaneous wind direction]
- **windspeedmph** - [mph instantaneous wind speed]
- **windgustmph** - [mph current wind gust, using software specific time period]
- **windgustdir** - [0-360 using software specific time period]
- **windspdmph_avg2m**  - [mph 2 minute average wind speed mph]
- **winddir_avg2m** - [0-360 2 minute average wind direction]
- **windgustmph_10m** - [mph past 10 minutes wind gust mph ]
- **windgustdir_10m** - [0-360 past 10 minutes wind gust direction]

### Response

Status Code

```
200
```

Response Body

```
success
```

### Examples

#### Example 1

Lets assume 10:00:00 time in a particular day, and a Rain Gauge is showing the Accumulative Precipitation value as 0.2 mm. 
Also consider the Rain Gauge's tipping  bucket size is 0.2 mm.
In sub-sequence time steps of 10:02:14, 10:04:10, 10:06:45 and 10:09:00, the Rain Gauge's tipping bucket is tipped and the
Accumulative Precipitation (Rainfall) is shown in the following graph.

```bash
Accumulative Precipitation (mm)
    ^
    |
1.0 |                                              __________________
0.8 |                                     ________|        !
0.6 |                   _________________|                 !
0.4 |          ________|        !                          !
0.2 |_________|                 !                          !
0.0 |___________________________!__________________________!_____________> (time)
    ^         ^        ^        ^        ^        ^        ^
    10:00:00 10:02:14 10:04:10 10:05:00 10:06:45 10:09:00 10:10:00
```

Lets say that, these data collected by an automated Weather station (only capable of measuring precipitation) and it is sending the data to a server in 5 minute intervals.
Also assume that the weather station is already uploaded the data at 10:00:00 and it wants to upload data in 10:05:00 and 10:10:00 
time steps. Then the two requests data should be as below.

**Request 1** (At `10:05:00`)
```json
{
    "ID": "curw_test",
    "PASSWORD": "XXX",
    "data": [{
        "dateutc": "2018-01-01 10:05:00",
        "dailyrainMM": "0.6",
        "rain": ["2018-01-01 10:02:14", "2018-01-01 10:04:10"]
    }],
    "health": {
        "batt": "3.96"
    },
    "action": "updateraw",
    "softwaretype": "iCon",
    "version": "1.3.6"
}
```
 
**Request 2** (At `10:10:00`)
```json
{
    "ID": "curw_test",
    "PASSWORD": "XXX",
    "data": [{
        "dateutc": "2018-01-01 10:10:00",
        "dailyrainMM": "1.0",
        "rain": ["2018-01-01 10:06:45", "2018-01-01 10:09:00"]
    }],
    "health": {
        "batt": "3.97"
    },
    "action": "updateraw",
    "softwaretype": "iCon",
    "version": "1.3.6"
}
```
**Notes**: Since this weather station is capable of measuring only Precipitation, other fields are ignored.
Further the Precipitation is measured in `mm` (millimeters), thus reporting Precipitation in `in` (inches) is ignored.

#### Example 2

Lets assume that the weather station mentioned in example 1, is modified and added the capability to measure the Temperature in Fahrenheit (not in Celsius)
as shown in the graph below,
 
```bash
Temperature (Fahrenheit)
    ^
    |
108 |             ,.........                                 
106 |         ...'       !  ',.........                         
104 |       ,'           !             ',     
102 |     ,'             !               ',...........          
100 |...,'               !                   !        
 98 |____________________!___________________!____________> (time)
    ^                    ^                   ^   
    10:00:00            10:05:00            10:10:00
```

Lets assume that Temperature values at 10:00:00 -> 98F, 10:05:00 -> 108 and 10:10:00 -> 102.
Then the two requests data should be as below.

**Request 1** (At `10:05:00`)
```json
{
    "ID": "curw_test",
    "PASSWORD": "XXX",
    "data": [{
        "dateutc": "2018-01-01 10:05:00",
        "dailyrainMM": "0.6",
        "rain": ["2018-01-01 10:02:14", "2018-01-01 10:04:10"],
        "tempf": "98"
    }],
    "health": {
        "batt": "3.96"
    },
    "action": "updateraw",
    "softwaretype": "iCon",
    "version": "1.3.6"
}
```
 
**Request 2** (At `10:10:00`)
```json
{
    "ID": "curw_test",
    "PASSWORD": "XXX",
    "data": [{
        "dateutc": "2018-01-01 10:10:00",
        "dailyrainMM": "1.0",
        "rain": ["2018-01-01 10:06:45", "2018-01-01 10:09:00"],
        "tempf": "102"
    }],
    "health": {
        "batt": "3.97"
    },
    "action": "updateraw",
    "softwaretype": "iCon",
    "version": "1.3.6"
}
```
**Notes**: Since this weather station is capable of only measuring Precipitation and Temperature, other fields are ignored.
Further Temperature is measured in `F` (Fahrenheit), thus reporting Temperature in `C` (Celsius) ignored.

#### Example 3

Lets consider the example 1 & 2 scenarios, but weather station is planing to upload the data in 10 minutes interval and
sample the data in 5 minutes interval (e.g. in order to save the battery while communicating over network).
In that case, the weather station will send one request at 10:10:00 (Ignoring sending at 10:05:00) after 10:00:00.
Then the request data should be as below.

**Request** (At `10:10:00`)
```json
{
    "ID": "curw_test",
    "PASSWORD": "XXX",
    "data": [{
        "dateutc": "2018-01-01 10:05:00",
        "dailyrainMM": "0.6",
        "rain": ["2018-01-01 10:02:14", "2018-01-01 10:04:10"],
        "tempf": "98"
    }, {
        "dateutc": "2018-01-01 10:10:00",
        "dailyrainMM": "1.0",
        "rain": ["2018-01-01 10:06:45", "2018-01-01 10:09:00"],
        "tempf": "102"
    }],
    "health": {
        "batt": "3.97"
    },
    "action": "updateraw",
    "softwaretype": "iCon",
    "version": "1.3.6"
}
```
**Notes**: Notice that there are two objects in the `data` list field.

#### Example 4

Lets consider the example 3, where weather station is planing to upload the data in 10 minutes interval and
sample the data in 5 minutes interval. Then the weather station will send one request at 10:10:00 (Ignoring sending at 10:05:00) after 10:00:00.
Also assume that there is not any Precipitation during that time (Accumulative Precipitation value remain unchanged as 0.2mm).
Then the request data should be as below.

**Request** (At `10:10:00`)
```json
{
    "ID": "curw_test",
    "PASSWORD": "XXX",
    "data": [{
        "dateutc": "1514801100",
        "dailyrainMM": "0.2",
        "rain": [],
        "tempf": "98"
    }, {
        "dateutc": "2018-01-01 10:10:00",
        "dailyrainMM": "0.2",
        "rain": [],
        "tempf": "102"
    }],
    "health": {
        "batt": "3.97"
    },
    "action": "updateraw",
    "softwaretype": "iCon",
    "version": "1.3.6"
}
```

**Notes**: It is using [UNIX Timestamp](https://www.unixtimestamp.com/index.php) `1514801100`, instead of `2018-01-01 10:05:00` date time string.
The `rain` field is an empty list, since there is not any ticks for given period.

### Common Pitfalls

All the date time should be in "YYYY-MM-DD HH:MM:SS" format.

**Okay**

- 2018-01-01 10:00:00

**Wrong**

- ~~2018-1-1 10:00:00~~
- ~~2018-1-1 10:0:0~~
- ~~2018/01/01 10:00:00~~
- ~~01/01/2018 10:00:00~~