from calibration.calibration import Calibration


def get_ylabel(calibration: Calibration, variable_name: str) -> str:
    label = calibration.dynamical_model.variable_name_to_label[variable_name]
    if variable_name == 'Ke':
        notation = 'K'
    elif variable_name == 'c':
        notation = 'S'
    elif len(variable_name) == 1:
        notation = variable_name.upper()
    else:
        notation = variable_name
    return f'{label} {notation}'
