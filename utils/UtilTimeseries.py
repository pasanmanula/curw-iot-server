def extract_single_variable_timeseries(timeseries, variable, opts=None):
    """
    Then Lines follows the data. This function will extract the given variable timeseries
    """
    if opts is None:
        opts = {}

    def precipitation(my_timeseries):
        print('precipitation:: PrecipitationMM')
        new_timeseries = []
        for t in my_timeseries:
            if t['PrecipitationMM'] is not None:
                new_timeseries.append([t['Time'], t['PrecipitationMM']])
        return new_timeseries

    def temperature(my_timeseries):
        print('temperature:: TemperatureC')
        new_timeseries = []
        for t in my_timeseries:
            if t['TemperatureC'] is not None:
                new_timeseries.append([t['Time'], t['TemperatureC']])
        return new_timeseries

    def default(my_timeseries):
        print('default', my_timeseries)
        return []

    variable_dict = {
        'Precipitation': precipitation,
        'Temperature': temperature,
    }
    return variable_dict.get(variable, default)(timeseries)
    # --END extract_single_variable_timeseries --
