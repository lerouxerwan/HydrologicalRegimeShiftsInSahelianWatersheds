from bifurcation.bifurcation import Bifurcation
from bifurcation.shift_range.shift_range import ShiftRange
from bifurcation.shift_range.shift_range_visualisation import InverseShiftRangeForPlots
from projects.paper_model.utils_paper_model import sahel_watershed_names, get_calibration


def get_watershed_name_to_shift_range_list(fast: bool) -> tuple[dict[str, list[ShiftRange]], dict[str, Bifurcation], dict[str, list[float]]]:
    # Limits for the ensemble
    watershed_name_to_l = {}
    watershed_name_to_bifurcation = {}
    watershed_name_to_annual_precipitation_values = {}
    for watershed_name in sahel_watershed_names:
        calibration = get_calibration(watershed_name, fast=False)
        annual_precipitation_values = [calibration.get_forcings(year)['p'] for year in range(1965, 2015)]
        watershed_name_to_annual_precipitation_values[watershed_name] = annual_precipitation_values
        bifurcation = Bifurcation(calibration)
        shift_range_list = [bifurcation_data.shift_range for bifurcation_data in
                            bifurcation.ensemble_id_to_bifurcation_data.values()
                            if bifurcation_data.is_bistable]
        shift_range_list = [InverseShiftRangeForPlots.from_shift_range(shift_range)
                            if shift_range.branches_are_crossing else shift_range
                            for shift_range in shift_range_list]
        watershed_name_to_l[watershed_name] = shift_range_list
        watershed_name_to_bifurcation[watershed_name] = bifurcation
    return watershed_name_to_l, watershed_name_to_bifurcation, watershed_name_to_annual_precipitation_values
