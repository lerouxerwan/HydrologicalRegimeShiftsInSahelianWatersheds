from matplotlib import pyplot as plt

from bifurcation.bifurcation import Bifurcation
from projects.paper_model.section_7_appendix.utils_compute_is_bistable import compute_percentage_bistable
from projects.paper_model.utils_paper_model import sahel_watershed_names, get_calibration
from utils.utils_plot import show_or_save_plot
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label


def main_plot_sensitivity_max_forcing(fast: bool, show: bool):
    ax = plt.gca()
    max_forcing_list = list(range(100, 4001))[::10]
    for watershed_name in sahel_watershed_names:
        # Extract data
        calibration = get_calibration(watershed_name, fast)
        bifurcation = Bifurcation(calibration)
        percentage_bistable = [compute_percentage_bistable(bifurcation, float(forcing)) for forcing in max_forcing_list]
        # Plot
        color = watershed_name_to_color[watershed_name]
        label = watershed_name_to_label[watershed_name]
        ax.plot(max_forcing_list, percentage_bistable, color=color, label=label)
    ax.set_xlabel('Maximum precipitation level to check bistability (mm)')
    ax.set_ylabel('Percentage of bistable ensemble members (%)')
    ax.set_xlim((max_forcing_list[0], max_forcing_list[-1]))
    # ax.set_ylim((-2, 102))
    ax.set_ylim((0, 100))
    ax.legend()
    show_or_save_plot(f'sensitivity_max_forcing', show)


if __name__ == '__main__':
    b = False
    main_plot_sensitivity_max_forcing(b, b)