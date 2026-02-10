import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from bifurcation.regime import compute_percentage_regime, Regime, RegimeDef, regime_def_to_name
from bifurcation.bifurcation import Bifurcation
from projects.paper_model.utils_paper_model import sahel_watershed_names, \
    get_calibration, \
    year_after, years_regime_shift, year_before
from utils.utils_log import log_info
from utils.utils_plot import show_or_save_plot, subplots_custom
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label


def main_plot_percentage_lower_area(fast=False, show=False):
    # Load once the bifurcation data
    watershed_name_to_bifurcation = {watershed_name: Bifurcation(get_calibration(watershed_name, fast))
                                     for watershed_name in sahel_watershed_names[:]}
    # Plot percentage of regime side by side
    fig, axs = subplots_custom(1, 2, sharey=False)
    for ax, regime_def in zip(axs, [RegimeDef.basin_attraction, RegimeDef.threshold]):
        log_info(f'Plot percentage lower area for {regime_def_to_name[regime_def]}')
        _main_plot_percentage_lower_area(ax, regime_def, watershed_name_to_bifurcation, fast, show)
    # Add (a) and (b) on each plot
    for letter, ax in zip('ab', axs):
        ymin, ymax = ax.get_ylim()
        y_text = ymin + 0.95 * (ymax - ymin)
        xmin, xmax = ax.get_xlim()
        x_text = xmin + 0.9 * (xmax - xmin)
        ax.text(x_text, y_text, f'({letter})', weight="bold", fontsize=10)
    show_or_save_plot(f'percentage_regimes', show)



def _main_plot_percentage_lower_area(ax: Axes, regime_def: RegimeDef, watershed_name_to_bifurcation, fast=False, show=False):
    for watershed_name in sahel_watershed_names[:]:
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        bifurcation = watershed_name_to_bifurcation[watershed_name]
        calibration = bifurcation.calibration
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
        if regime_def == RegimeDef.basin_attraction:
            pass
        else:
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
    ylabel = 'Selected parameterization in the\n"High runoff coefficient regime" (%)'
    ax.set_ylabel(ylabel)
    ax.xaxis.grid()
    ax.legend(loc='center right')

    # Add legend for the two lines
    ax_twin = ax.twiny()
    ylabel = 'Selected parameterization\nin the "High runoff\ncoefficient regime" (%)'
    new_handles = [
        Line2D([], [], color='k', marker='None', label=ylabel, linestyle='-'),
        Line2D([], [], color='k', marker='None', label="Year of regime shift", linestyle='dotted'),
    ]
    if regime_def == RegimeDef.basin_attraction:
        new_handles = new_handles[:1]
    legend = ax_twin.legend(handles=new_handles, loc='lower right')
    legend.get_title().set_multialignment('center')
    ax_twin.set_xticks([])

if __name__ == '__main__':
    main_plot_percentage_lower_area(False, False)
