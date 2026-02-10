from collections import OrderedDict

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

from calibration.utils_calibration.convert import get_year_from_time
from projects.paper_model.utils_paper_model import get_calibration, sahel_watershed_names
from utils.utils_watershed import watershed_name_to_label


def get_ensemble_id_to_couples(watershed_name: str, fast):
    calibration = get_calibration(watershed_name, fast)
    observation_constraint = calibration.observation_constraint
    dynamical_model = calibration.dynamical_model
    constraint_name = observation_constraint.constraint_names[0]
    years = [get_year_from_time(time) for time in calibration.times]
    index_to_year = {index: year for index, year in enumerate(years) if year in observation_constraint.year_to_index}
    ensemble_id_to_couples = {}
    for ensemble_id in calibration.ensemble_ids:
        params = calibration.ensemble_id_to_params[ensemble_id]
        state_vectors = calibration.ensemble_id_to_state_vectors[ensemble_id]
        assert len(state_vectors) == len(years)
        couples = []
        for index, year in index_to_year.items():
            simulated_value = dynamical_model.get_variable(constraint_name, calibration.get_forcings(year),
                                                           dynamical_model.create_states(
                                                               state_vectors[index]), params)
            observed_value = observation_constraint.get_constraint_value(constraint_name, year)
            couple = (observed_value, simulated_value)
            couples.append(couple)
        ensemble_id_to_couples[ensemble_id] = couples
    return ensemble_id_to_couples

def compute_metric(couples):

    return

def compute_nse(predictions, targets):
    return 1 - (np.sum((targets - predictions) ** 2) / np.sum((targets - np.mean(targets)) ** 2))



def main_more_metrics(fast: bool, show: bool):
    d_watershed = OrderedDict()
    for watershed_name in sahel_watershed_names[:]:
        metrics_list = []
        for couples in get_ensemble_id_to_couples(watershed_name, fast).values():
            observed_values, simulated_values = list(zip(*couples))
            observed_values, simulated_values = np.array(observed_values), np.array(simulated_values)
            metrics = [
                compute_nse(simulated_values, observed_values),
                mean_squared_error(observed_values, simulated_values, squared=False),
                np.mean(simulated_values) - np.mean(observed_values),
            ]
            metrics_list.append(metrics)
        nse, rmse, bias = list(zip(*metrics_list))
        d = {
            'Bias': bias,
            'NSE': nse,
            'RMSE': rmse,
        }
        df = pd.DataFrame.from_dict(d)
        # df = df.describe().loc[['min', 'mean', 'max']].round(2)
        df = df.describe().loc[['min', 'mean', 'max']].round(3)

        d_watershed[watershed_name_to_label[watershed_name]] = df.apply(lambda s: f"{s['mean']} ({s['min']},{s['max']})", axis=0)

    df_all = pd.DataFrame.from_dict(d_watershed).transpose()
    print_df_latex(df_all)





def print_df_latex(df: pd.DataFrame, index: bool = True):
    column_format = ''.join(['c' for _ in df.columns])
    if index:
        column_format += 'c'
    s_latex = df.to_latex(index=index, column_format=column_format, float_format="%.2f")
    s = ') \\\\'
    s_latex = s_latex.replace(s, s + ' \\hline ')
    for s in ['\\midrule', '\\toprule']:
        s_latex = s_latex.replace(s, '\\hline \\hline ' + s)
    print('\n\n', s_latex, '\n\n')



# def compute_error(self, state_vectors_and_params: tuple[np.ndarray, dict[str, float]]) -> float:
#     state_vectors, params = state_vectors_and_params
#     sum_of_squared_errors = 0
#     nb_obs = 0
#     #  Loop on the constraints
#     for constraint_name in self.observation_constraint.constraint_names:
#         for time, state_vector in zip(self.times, state_vectors):
#             year =
#             if year in self.observation_constraint.year_to_index:
#                 constraint_value = self.observation_constraint.get_constraint_value(constraint_name, year)
#                 if not np.isnan(constraint_value):
#                     model_value = self.dynamical_model.get_variable(constraint_name, self.get_forcings(year),
#                                                                     self.dynamical_model.create_states(
#                                                                         state_vector), params)
#                     assert isinstance(model_value, float)
#                     sum_of_squared_errors += (model_value - constraint_value) ** 2
#                     nb_obs += 1
#     assert nb_obs > 0
#     return np.sqrt(sum_of_squared_errors / nb_obs)


if __name__ == '__main__':
    main_more_metrics(fast=False)