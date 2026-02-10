import matplotlib.pyplot as plt

from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint
from calibration.observation_constraint.runoff.runoff_constraint import RunoffObservationConstraintForPlotsOnly
from projects.paper_model.utils_paper_model import sahel_watershed_names
from utils.utils_plot import save_plot, show_or_save_plot, subplots_custom
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label

FONTSIZE_LABEL = 12


def plot_rain_data(fast=False, show=False):
    ax = plt.gca()
    _plot_rain_data(ax)
    show_or_save_plot('rain', show)


def plot_runoff_data(fast=False, show=False):
    ax = plt.gca()
    _plot_runoff_data(ax)
    show_or_save_plot('discharge', show)


def plot_runoff_coefficient_data(fast=False, show=False):
    ax = plt.gca()
    _plot_runoff_coefficient_data(ax)
    show_or_save_plot('runoff_coefficient', show)

# This order is adapted for the precipitation plot (Nakanbe at the top of the legend because it has more precipitation)
sahel_watershed_names_ordered_for_the_plot = sahel_watershed_names[::-1]


def _plot_rain_data(ax):
    for watershed_name in sahel_watershed_names_ordered_for_the_plot:
        forcing_function = RainObsForcingFunction(watershed_name)
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        forcing_function.plot_forcing_function(ax, color=color, label=label, linestyle=None, marker='x',
                                               fontsize=FONTSIZE_LABEL)
    ax.legend()
    ax.grid()
    # Set limits
    ax.set_xlim((1956, 2015))
    ax.set_ylim((200, 900))
    ax.set_xlabel('Years', fontsize=FONTSIZE_LABEL)


def _plot_runoff_data(ax):
    for watershed_name in sahel_watershed_names_ordered_for_the_plot:
        observation_constraint = RunoffObservationConstraintForPlotsOnly(watershed_name, final_year=2015)
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        observation_constraint.plot_observation_constraint(ax, user_label=label, user_color=color)
    ax.legend()
    ax.grid()
    # Set limits
    ax.set_xlim((1956, 2015))
    ax.set_ylim((0, 140))
    ax.set_xlabel('Years')
    ax.set_ylabel('Discharge ($m^3 s^{-1}$)', fontsize=FONTSIZE_LABEL)


def _plot_runoff_coefficient_data(ax):
    for watershed_name in sahel_watershed_names_ordered_for_the_plot:
        observation_constraint = RunoffCoefficientObservationConstraint(watershed_name, final_year=2015)
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        observation_constraint.plot_observation_constraint(ax, user_label=label, user_color=color)
    ax.legend()
    ax.grid()
    # Set limits
    ax.set_xlim((1956, 2015))
    ax.set_ylim((0, 0.25))
    ax.set_xlabel('Years', fontsize=FONTSIZE_LABEL)
    ax.set_ylabel('Runoff coefficient K (-)', fontsize=FONTSIZE_LABEL)


def plot_data(fast=False, show=False):
    fig, (ax1, ax2) = subplots_custom(1, 2, wspace=0.15)
    _plot_rain_data(ax1)
    _plot_runoff_coefficient_data(ax2)
    for letter, ax in zip('ab', [ax1, ax2]):
        ymin, ymax = ax.get_ylim()
        y_text = ymin + 0.9 * (ymax - ymin)
        ax.text(2005, y_text, f'({letter})', weight="bold", fontsize=10)
    show_or_save_plot('data', show)


if __name__ == '__main__':
    b = False
    plot_data(b, b)
    # plot_runoff_data()
    # plot_runoff_coefficient_data()
