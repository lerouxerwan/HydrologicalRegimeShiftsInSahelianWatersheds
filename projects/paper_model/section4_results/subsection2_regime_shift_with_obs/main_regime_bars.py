import numpy as np

from bifurcation.regime import Regime, regime_to_name, compute_regime_counter
from bifurcation.bifurcation import Bifurcation
from projects.paper_model.utils_paper_model import sahel_watershed_names, get_calibration
from utils.utils_plot import show_or_save_plot, subplots_custom
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label

YEARS = [1965, 2014]


def plot_regimes(ax, year, fast=False, vertical=True):
    regimes = [Regime.lower, Regime.upper]
    regime_names = [regime_to_name[regime] for regime in regimes]

    width = 0.2  # the width of the bars
    multiplier = 0
    locations = np.arange(len(regime_names))  # the label locations

    for watershed_name in sahel_watershed_names:
        calibration = get_calibration(watershed_name, fast)
        bifurcation = Bifurcation(calibration)
        regime_counter = compute_regime_counter(bifurcation, calibration, year)
        percentage_lower_area, percentage_upper_area = [100 * regime_counter[regime] / calibration.ensemble_size
                                                        for regime in [Regime.lower, Regime.upper]]
        if vertical:
            regime_repartition = (percentage_lower_area, percentage_upper_area)
        else:
            regime_repartition = (percentage_upper_area, percentage_lower_area)
        print(watershed_name, year, percentage_lower_area, percentage_upper_area)
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        offset = width * multiplier
        bar_function = ax.bar if vertical else ax.barh
        bar_function(locations + offset, regime_repartition, width, label=label, color=color)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Regime repartition in {}'.format(year))
    tick_function = ax.set_xticks if vertical else ax.set_yticks
    tick_regime_names = regime_names if vertical else [n.replace('off ', 'off    \n') for n in regime_names]
    tick_function(locations + 1.5 * width, tick_regime_names, rotation=0 if vertical else 90)
    if not vertical:
        for label in ax.yaxis.get_ticklabels():
            label.set_verticalalignment('center')
    limit_function = ax.set_ylim if vertical else ax.set_xlim
    limit_function(0, 100)

    #  Some parameters
    axis = ax.yaxis if vertical else ax.xaxis
    axis.grid()
    if vertical:
        loc = 'upper left' if year != 1965 else 'upper right'
    else:
        loc = 'upper right' if year != 1965 else 'lower right'
    ax.legend(loc=loc, prop={'size': 8})
    label_function = ax.set_ylabel if vertical else ax.set_xlabel
    label_function('Percentage of ensemble members (%)')

    #  Straight lines
    for value in [1 - width]:
        line_function = ax.axvline if vertical else ax.axhline
        line_function(value, -.3, 1., linestyle='dashed', color='gray', linewidth=2)


def main_plot_regimes(fast=False, show=False):
    fig, axs = subplots_custom(1, 2, wspace=0.1)
    fig.patch.set_facecolor('white')
    fig.patch.set_alpha(1.0)
    for ax, year in zip(axs, YEARS):
        plot_regimes(ax, year, fast, vertical=False)
    show_or_save_plot('calibration_regime', show)


if __name__ == '__main__':
    b = False
    main_plot_regimes(b, b)
