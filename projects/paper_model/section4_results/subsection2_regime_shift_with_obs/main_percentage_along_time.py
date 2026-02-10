import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from bifurcation.regime import compute_percentage_regime, Regime, RegimeDef, regime_def_to_name
from bifurcation.bifurcation import Bifurcation
from projects.paper_model.utils_paper_model import sahel_watershed_names, \
    get_calibration, \
    year_after, years_regime_shift, year_before
from utils.utils_log import log_info
from utils.utils_plot import show_or_save_plot
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label


def main_plot_percentage_lower_area(fast=False, show=False):
    for regime_def in [RegimeDef.basin_attraction, RegimeDef.threshold][:]:
        log_info(f'Plot percentage lower area for {regime_def_to_name[regime_def]}')
        _main_plot_percentage_lower_area(regime_def, fast, show)


def _main_plot_percentage_lower_area(regime_def: RegimeDef, fast=False, show=False):
    ax = plt.gca()
    for watershed_name in sahel_watershed_names[:]:
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        calibration = get_calibration(watershed_name, fast)
        bifurcation = Bifurcation(calibration)
        #   Display the number of monostable ensemble_ids
        percentage_monostable_members = 100 * (len(bifurcation.monostable_ensemble_ids) / len(bifurcation.ensemble_ids))
        log_info(f'Percentage of monostable members {percentage_monostable_members}')
        # Compute percentage of regime
        percentages = [compute_percentage_regime(bifurcation, calibration, year, Regime.upper, regime_def)
                       for year in years_regime_shift]
        # print first year when the percentage is above 50%
        # for year, percentage in zip(years_regime_shift, percentages):
        #     if percentage > 50:
        #         print(watershed_name, year, percentage)
        #         ax.axvline(x=year, ymin=0, ymax=0.5, linestyle='dashed', color=color, linewidth=2)
        #         break
        # print the year with maximal derivative, i.e. the increase, is maximal
        max_derivative = 0
        year_with_max_derivative = np.nan
        for year_in_middle, previous_percentage, next_percentage in zip(years_regime_shift[1:], percentages, percentages[2:]):
            derivative = next_percentage - previous_percentage
            if derivative > max_derivative:
                max_derivative = derivative
                year_with_max_derivative = year_in_middle
        ax.axvline(x=year_with_max_derivative, ymin=0, ymax=1.0, linestyle='dotted', color=color, linewidth=2)
        log_info(f'Year with max derivative = {year_with_max_derivative} for {watershed_name}')

        # print the main curve
        ax.plot(years_regime_shift, percentages, label=label, color=color)

    # plt.axhline(y=50, xmin=0, xmax=1, linestyle='dashed', color='k', linewidth=2)
    ax.set_xlim((year_before, year_after))
    ax.set_xticks([year for year in years_regime_shift if year % 5 == 0])
    ax.set_xlabel('Years')
    ax.set_ylim((0, 100))
    ax.set_yticks([10 * i for i in range(11)])
    ylabel = 'Ensemble members in the\n"High runoff coefficient regime" (%)'
    ax.set_ylabel(ylabel)
    ax.xaxis.grid()
    ax.legend(loc='center right')

    # Add legend for the two lines
    ax_twin = ax.twiny()
    ylabel = 'Ensemble members\nin the "High runoff\ncoefficient regime" (%)'
    new_handles = [
        Line2D([], [], color='k', marker='None', label=ylabel, linestyle='-'),
        Line2D([], [], color='k', marker='None', label="Year of regime shift", linestyle='dotted'),
    ]
    legend = ax_twin.legend(handles=new_handles, loc='lower right')
    legend.get_title().set_multialignment('center')
    ax_twin.set_xticks([])

    show_or_save_plot(f'obs_forcing_{regime_def_to_name[regime_def]}', show)


if __name__ == '__main__':
    b = False
    main_plot_percentage_lower_area(b, False)
