import numpy as np
from matplotlib.lines import Line2D

from calibration.utils_calibration.convert import load_times
from calibration.utils_calibration.plot import get_ylabel
from projects.paper_model.utils_paper_model import get_calibration, \
    sahel_watershed_names
from utils.utils_plot import show_or_save_plot, subplots_custom
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label


def main_plot_trajectory(fast=False, show=False):
    fig, axs = subplots_custom(2, 2, sharey='row', sharex='col', hspace=0.1, wspace=0.1)
    for i, variable_name in enumerate(['c', 'Ke'][::-1]):
        for j in range(2):
            indexes = [0, 3] if j == 1 else [1, 2]
            letter = 'abcd'[i * 2 + j]
            watershed_names = [sahel_watershed_names[k] for k in indexes]
            plot_trajectory(axs[i, j], variable_name, watershed_names, letter, fast)
    # Set same x_lim for the second column
    x_lim = axs[0, 0].get_xlim()
    for ax in axs[:, 1]:
        ax.set_xlim(x_lim)
    show_or_save_plot('calibration_trajectory', show)


def main_plot_trajectory_for_slide(fast=False, show=False):
    fig, axs = subplots_custom(1, 2, sharey='row', sharex='col', hspace=0.1, wspace=0.1)
    for i, variable_name in enumerate(['Ke']):
        for j in range(2):
            indexes = [0, 3] if j == 1 else [1, 2]
            watershed_names = [sahel_watershed_names[k] for k in indexes]
            plot_trajectory(axs[j], variable_name, watershed_names, '', fast, True)
    show_or_save_plot('calibration_trajectory_slide', show)


def plot_trajectory(ax, variable_name, watershed_names, letter, fast=False, for_slide=False):
    min_time = 2015
    for watershed_name in watershed_names:

        calibration = get_calibration(watershed_name, fast)

        #  Plot all the trajectories
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        times = load_times(calibration.initial_year, calibration.final_year)
        all_variables = calibration.get_all_variables(variable_name, calibration.initial_year, calibration.final_year)
        mean_variables = np.mean(all_variables, axis=0)
        lower_bound, upper_bound = [np.quantile(all_variables, q, axis=0) for q in [0.05, 0.95]]
        ax.fill_between(times, lower_bound, upper_bound, color=color, alpha=0.4)
        ax.plot(times, mean_variables, color=color, label=label)
        min_time = min(min_time, times[0])

        if variable_name == "Ke":
            calibration.observation_constraint.plot_observation_constraint(ax, user_label=False,
                                                                           user_color=color)
    #  Some parameters
    ax.grid()
    fontsize = 12
    ax.set_ylabel('{} (-)'.format(get_ylabel(calibration, variable_name)), fontsize=fontsize)
    ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.01)
    ax.set_xlim((min_time, 2015))
    if not for_slide:
        ax.text(1985, 0.9 * ax.get_ylim()[1], f'({letter})', weight="bold", fontsize=10)
        loc = "upper right" if variable_name == "c" else "upper left"
        ax.legend(loc=loc)
    ax.set_xlabel('Years')
    if for_slide:
        # Add some custom legend to explain observations, ensemble mean, and ensemble range
        ax_twin = ax.twiny()
        ax_twin.fill_between([], [], [], color='k', alpha=0.4, label='Ensemble spread (5th and 95th percentile)')
        new_handles = [
            Line2D([], [], color='k', marker='o', label="Observations", linestyle='None'),
            Line2D([], [], color='k', marker='None', label="Ensemble mean", linestyle='-'),
            ax_twin.get_legend_handles_labels()[0][0],
        ]
        ax_twin.legend(handles=new_handles, loc='upper left')
        ax_twin.set_xticks([])


if __name__ == '__main__':
    b = False
    main_plot_trajectory(b, b)
    # main_plot_trajectory_for_slide(b,b)
