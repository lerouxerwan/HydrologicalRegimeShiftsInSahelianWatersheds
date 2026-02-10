import itertools
from copy import copy

import matplotlib.pyplot as plt
import numpy as np

from calibration.calibration import Calibration
from calibration.utils_calibration.convert import load_times
from calibration.utils_calibration.plot import get_ylabel
from utils.utils_plot import save_plot, show_or_save_plot
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label


def plot_mean_trajectory(calibration, watershed_name, variable_name, show=False):
    ax = plt.gca()

    #  Plot all the trajectories
    color = watershed_name_to_color[watershed_name]
    label = watershed_name_to_label[watershed_name]
    times = load_times(calibration.initial_year, calibration.final_year)
    all_variables = calibration.get_all_variables(variable_name, calibration.initial_year, calibration.final_year)
    mean_variables = np.mean(all_variables, axis=0)
    lower_bound, upper_bound = [np.quantile(all_variables, q, axis=0) for q in [0.05, 0.95]]
    ax.fill_between(times, lower_bound, upper_bound, color=color, alpha=0.4)
    ax.plot(times, mean_variables, color=color, label=label)

    if variable_name == "Ke":
        calibration.observation_constraint.plot_observation_constraint(ax, user_label=False,
                                                                       user_color=color)
    #  Some parameters
    ax.grid()
    fontsize = 12
    ax.set_ylabel('{} (-)'.format(get_ylabel(calibration, variable_name)), fontsize=fontsize)
    ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.01)
    ax.set_xlim((1950, 2015))
    loc = "upper right" if variable_name == "c" else "upper left"
    ax.legend(loc=loc)
    ax.set_xlabel('Years')
    show_or_save_plot(f'trajectory_{variable_name}_{watershed_name}', show)

def plot_relationship_between_parameters(calibration: Calibration):
    parameter_names_with_range = list(calibration.dynamical_model.parameter_name_to_range.keys())
    for parameter_name_1, parameter_name_2 in itertools.combinations(parameter_names_with_range, r=2):
        ax = plt.gca()
        parameter_values_1 = [params[parameter_name_1] for params in calibration.ensemble_id_to_params.values()]
        parameter_values_2 = [params[parameter_name_2] for params in calibration.ensemble_id_to_params.values()]
        ax.scatter(parameter_values_1, parameter_values_2)
        ax.set_xlabel(parameter_name_1)
        ax.set_ylabel(parameter_name_2)
        ax.set_title(calibration.name)
        show_or_save(calibration, 'relationship_{}_{}'.format(parameter_name_1, parameter_name_2))


def plot_rmse_for_all_range_parameters(calibration: Calibration):
    #  Load parameters
    params_list, _, error_list = calibration.solve_data
    for parameter_name, parameter_range in calibration.dynamical_model.parameter_name_to_range.items():
        ax = plt.gca()
        ax.scatter([params[parameter_name] for params in params_list], error_list)
        ax.scatter([params[parameter_name] for params in params_list], error_list, color='r')
        ax.set_xlim(parameter_range)
        ax.set_ylabel('RMSE')
        ax.set_xlabel(parameter_name)
        title = calibration.name + ' Error={}'.format(np.round(np.mean(error_list), decimals=3))
        ax.set_title(title)
        show_or_save(calibration, 'rmse_{}'.format(parameter_name))


def plot_trajectory_ensemble(calibration: Calibration, final_year_for_plot=None):
    """
    Plot the trajectory of the ensemble params
    :param calibration: Calibration to plot
    :param final_year_for_plot: final_year for the plot, by default if final_year=None we rely on the years.
    """
    ax = plt.gca()
    _plot_trajectory_ensemble(calibration, ax, final_year_for_plot)
    end_trajectory_plot(calibration, ax)


def _plot_trajectory_ensemble(calibration: Calibration, ax, final_year_for_plot=None):
    ax_twin = ax.twinx()
    #  Load final year
    if final_year_for_plot is None:
        final_year_for_plot = calibration.final_year
    assert isinstance(final_year_for_plot, int)
    times_plot = load_times(calibration.initial_year, final_year_for_plot)
    #  Plot forcing
    calibration.forcing_function.plot_forcing_function(ax_twin, calibration.years)
    ax_twin.legend(loc='upper right')
    #  Plot constraint
    calibration.observation_constraint.plot_observation_constraint(ax)
    #  Plot all the trajectories
    #  Plot states for all trajectories
    list_variable_name_to_variables = []
    for ensemble_id in calibration.ensemble_ids:
        params = calibration.ensemble_id_to_params[ensemble_id]
        states_list = calibration.ensemble_id_to_states_list[ensemble_id]
        variable_name_to_variables = calibration.dynamical_model.plot_dynamical_model(ax, times_plot, params,
                                                                                      states_list[:len(times_plot)])
        list_variable_name_to_variables.append(variable_name_to_variables)
    #  Plot the mean trajectory
    for variable_name in list_variable_name_to_variables[0].keys():
        list_variables = [variable_name_to_variables[variable_name]
                          for variable_name_to_variables in list_variable_name_to_variables]
        mean_variables = np.mean(np.array(list_variables), axis=0)
        calibration.dynamical_model.plot_variable(ax, times_plot, mean_variables[:len(times_plot)], variable_name,
                                                  highlight=True)


def end_trajectory_plot(calibration, ax):
    #  Create labels (remove items that are present several times in the legend)
    handles, labels = ax.get_legend_handles_labels()
    nb_variables_plot = len(set(labels))
    handles, labels = handles[-nb_variables_plot:], labels[-nb_variables_plot:]
    #   Add some potential marker on the label of the legend
    for i, (handle, label) in enumerate(zip(handles, labels)):
        handle = copy(handles[i])
        variable_name = calibration.dynamical_model.label_to_variable_name[label]
        if variable_name in calibration.observation_constraint.constraint_names:
            handle.set_marker(calibration.observation_constraint.constraint_name_to_marker[variable_name])
        handles[i] = handle
    ax.legend(handles, labels, loc="upper left")
    ax.set_xlim(calibration.times[0], calibration.times[-1])
    ax.set_ylim((0, 1))
    ax.set_ylabel('Ratio (-)')
    ax.set_xlabel('Year')
    show_or_save(calibration, 'trajectory_ensemble')


def show_or_save(calibration: Calibration, specific_name=''):
    if calibration.show:
        plt.show()
    else:
        plot_name = calibration.name
        #  In order to have a shorter filename
        if 'parameters' in plot_name:
            plot_name = plot_name.split('using')[0]
        plot_name += '_' + specific_name
        save_plot(plot_name)
