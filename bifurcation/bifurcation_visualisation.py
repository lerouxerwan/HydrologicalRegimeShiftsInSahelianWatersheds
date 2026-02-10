import matplotlib.pyplot as plt
import numpy as np

from bifurcation.regime import Regime, regime_to_name
from bifurcation.bifurcation import Bifurcation
from bifurcation.bifurcation_data.attractor_functions import get_attractors
from bifurcation.bifurcation_data.bifurcation_data import BifurcationData
from bifurcation.bifurcation_data.bistability_functions import is_bistable
from bifurcation.shift_range.shift_range import ShiftRange
from bifurcation.shift_range.shift_range_visualisation import plot_shift_range_marker, \
    plot_ticks_shift_range
from calibration.calibration import Calibration
from calibration.calibration_visualisation import show_or_save
from calibration.utils_calibration.plot import get_ylabel


def plot_bifurcation_diagram(bifurcation: Bifurcation, ensemble_id: int,
                             variable_name: str, min_forcing: float, max_forcing: float):
    bifurcation_data = bifurcation.ensemble_id_to_bifurcation_data[ensemble_id]
    calibration = bifurcation.calibration
    ax = plt.gca()
    forcings = np.arange(min_forcing, stop=max_forcing + 1)
    if variable_name == 'Ke':
        ax.set_ylim((0, 0.18))
    else:
        ax.set_ylim((0, 0.7))
    ax.set_xlim((forcings[0], forcings[-1]))

    #  Main plotting function the bifurcation graph
    _plot_bifurcation_graph(calibration, ax, variable_name, forcings, ensemble_id, bifurcation_data)

    _plot_shift_range(ax, bifurcation_data, forcings, calibration, variable_name, ensemble_id)

    _end_attractor_plot(calibration, ax, bifurcation_data, forcings, variable_name,
                        str(ensemble_id))


def _plot_shift_range(ax, bifurcation_data: BifurcationData, forcing_list, calibration, variable_name, ensemble_id, shift_range_definition: int = 1):
    if shift_range_definition == 1:
        _plot_shift_range_our_definition(ax, bifurcation_data.shift_range, forcing_list, calibration, variable_name, ensemble_id)
    elif shift_range_definition == 0:
        _plot_shift_range_classical_definition(ax, bifurcation_data.shift_range, forcing_list, calibration, variable_name, ensemble_id,
                                               bifurcation_data.forcing_to_repulsor)


def _plot_shift_range_classical_definition(ax, shift_range: ShiftRange, forcing_list, calibration, variable_name, ensemble_id, forcing_to_repulsor):
    # Plot separation line (two vertical lines, and one line following the repulsors)
    color = 'orange'
    linewidth = 2
    ax.axvline(x=shift_range.forcing_upper_state, ymin=shift_range.upper_state_value, ymax=1.0, linestyle='dashed', color=color, linewidth=linewidth)
    ax.axvline(x=shift_range.forcing_lower_state, ymin=0.0, ymax=shift_range.lower_state_value, linestyle='dashed', color=color, linewidth=linewidth)
    forcing_list = list(forcing_to_repulsor.keys())
    repulsors = list(forcing_to_repulsor.values())
    ax.plot(forcing_list, repulsors, linestyle='dashed', color=color, linewidth=linewidth, label='Separation of the two regimes')
    #  Plot regime names
    regimes = [Regime.upper, Regime.lower]
    for i, regime in enumerate(regimes):
        regime_name = regime_to_name[regime]
        if i == 0:
            x = 50
            y = 0.08
        else:
            x = 800
            y = 0.25
        ax.text(x, y, regime_name, fontsize=7, weight='bold')
    ax.legend(loc='upper left')


def _plot_shift_range_our_definition(ax, shift_range, forcing_list, calibration, variable_name, ensemble_id):

    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    # Plot separation line
    if variable_name in calibration.dynamical_model.state_names:
        plot_shift_range_marker(ax, shift_range, add_label=True, size=100)
        plot_ticks_shift_range(ax, shift_range, size=15)
        points = [shift_range.middle_state_value for _ in forcing_list]
    else:
        points = [
            calibration.get_variable(variable_name, ensemble_id, forcing, np.array([shift_range.middle_state_value]))
            for forcing in forcing_list]

    ax.plot(forcing_list, points, linestyle='dashed', color='orange', linewidth=2, label='Separation of the two regimes')
    #  Plot regime names
    regimes = [Regime.upper, Regime.lower]
    for i, regime in enumerate(regimes):
        regime_name = regime_to_name[regime]
        if variable_name in calibration.dynamical_model.state_names:
            x = xmin + 0.57 * (xmax - xmin)
            y = (shift_range.middle_state_value - 0.01) + (ymax - ymin) * 0.03 * (-1 if i == 0 else +1)
        else:
            x = xmin + (xmax - xmin) * (0.02 if i == 0 else 0.7)
            y = np.mean([ymin, ymax])
        ax.text(x, y, regime_name, fontsize=7, weight='bold')
    ax.legend(loc='upper left')


def _plot_bifurcation_graph(calibration: Calibration, ax,
                            variable_name: str, forcing_list: np.ndarray,
                            ensemble_id: int, bifurcation_data: BifurcationData):
    #  Setting to plot attractor/repulsor lines
    color, linewidth, label = 'k', 3, 'Attractors'
    params = calibration.ensemble_id_to_params[ensemble_id]
    attractors_list = [get_attractors(calibration.dynamical_model, params, forcing, calibration.solver_method) for forcing in forcing_list]
    if bifurcation_data.is_bistable:
        lower_bound, upper_bound = bifurcation_data.stability_ranges[0]
        if np.isnan(upper_bound):
            upper_bound = max(forcing_list)
        error_name = 'augment the range of forcings to incorporate ' \
                     'the bistability range ({} {})'.format(lower_bound, upper_bound)
        assert max(forcing_list) > lower_bound, error_name
        assert min(forcing_list) < upper_bound, error_name
        plot_attractor_branch(attractors_list, ax, calibration, color, ensemble_id, forcing_list, linewidth,
                              lower_bound, upper_bound, variable_name, label)
        #  Repulsor
        forcings_for_repulsors = list(bifurcation_data.forcing_to_repulsor.keys())
        repulsors = list(bifurcation_data.forcing_to_repulsor.values())
        variables = [calibration.get_variable(variable_name, ensemble_id, forcing, np.array([repulsor]))
                     for forcing, repulsor in zip(forcings_for_repulsors, repulsors)]
        ax.plot(forcings_for_repulsors, variables, color=color, linestyle="dotted", linewidth=linewidth,
                label='Repellers')
    else:
        state_vectors = [attractors[0] for attractors in attractors_list]
        states_list = [calibration.dynamical_model.create_states(state_vector) for state_vector in state_vectors]
        forcings_list = [calibration.forcing_function.create_forcings([forcing]) for forcing in forcing_list]
        variables = [calibration.dynamical_model.get_variable(variable_name, forcings, states, params)
                     for forcings, states in zip(forcings_list, states_list)]
        ax.plot(forcing_list, variables, color='k', linewidth=linewidth, label=label)
    ax.legend(loc='upper left')


def plot_attractor_branch(attractors_list, ax, calibration, color, ensemble_id, forcing_list, linewidth, lower_bound,
                          upper_bound, variable_name, label):
    bistability_branch_to_data = dict()
    #  Lower branch
    bistability_branch_to_data[False] = [(attractors[0], forcing)
                                         for attractors, forcing in zip(attractors_list, forcing_list) if
                                         forcing < upper_bound]
    #  Upper branch
    bistability_branch_to_data[True] = [
        (attractors[1], forcing) if is_bistable(attractors) else (attractors[0], forcing)
        for attractors, forcing in zip(attractors_list, forcing_list) if lower_bound < forcing]
    for bistability_branch, branch_data in bistability_branch_to_data.items():
        state_vectors, branch_forcings = list(zip(*branch_data))
        variables = [calibration.get_variable(variable_name, ensemble_id, forcing, state_vector)
                     for forcing, state_vector in zip(branch_forcings, state_vectors)]
        actual_label = label if bistability_branch else None
        ax.plot(branch_forcings, variables, color=color, linewidth=linewidth, label=actual_label)


def _end_attractor_plot(calibration, ax, bifurcation_data, forcings, variable_name, specific_name=""):
    #  Some settings for the plot
    bistable_to_label = {False: 'monostable', True: 'bistable'}
    bistable_label = bistable_to_label[bifurcation_data.is_bistable]
    ax.grid()
    add_bifurcation_labels(ax, calibration, variable_name)
    specific_name = "{}_{}_{}".format(specific_name, bistable_label, variable_name)
    show_or_save(calibration, specific_name)


def add_bifurcation_labels(ax, calibration, variable_name=None):
    if variable_name is None:
        variable_name = calibration.dynamical_model.state_names[0]
    fontsize = 12
    ax.set_ylabel('{} (-)'.format(get_ylabel(calibration, variable_name)), fontsize=fontsize)
    ax.set_xlabel(calibration.dynamical_model.forcing_function.y_label, fontsize=fontsize)
