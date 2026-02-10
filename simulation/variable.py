from enum import Enum


class Variable(Enum):
    """Define specific type of climate variables (temperature, precipitation, ...)"""
    PRECIP = 'pr'
    TEMP = 'tas'
    TEMP_MAX = 'tas_max'
    HUMID = 'hurs'
    HUMID_MAX = 'hurs_max'


variable_to_str = {
    Variable.PRECIP: 'pr',
    Variable.TEMP: 'tas',
    Variable.TEMP_MAX: 'tas_max',
    Variable.HUMID: 'hurs',
    Variable.HUMID_MAX: 'hurs_max',
}

ERA5_VARIABLES = [Variable.TEMP, Variable.TEMP_MAX, Variable.HUMID, Variable.HUMID_MAX]
