import seaborn as sns

from projects.paper_model.section4_results.subsection1_calibration.utils_distribution import \
    get_watershed_name_to_shift_range_list
from utils.utils_plot import show_or_save_plot, subplots_custom
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label


def main_delta_p_distribution(fast=False, show=False):
    fig, axs = subplots_custom(1, 2)
    # Limits for the ensemble
    watershed_name_to_l, _, _ = get_watershed_name_to_shift_range_list(fast)
    #  Show plots
    for i in range(2):
        ax = axs[i]
        for watershed_name, shift_range_list in watershed_name_to_l.items():
            if i == 1:
                values = [shift_range.forcing_lower_state for shift_range in shift_range_list]
            else:
                values = [shift_range.forcing_upper_state for shift_range in shift_range_list]
            sns.kdeplot(values, bw_adjust=0.7,
                        color=watershed_name_to_color[watershed_name],
                        label=watershed_name_to_label[watershed_name], ax=ax)

        symbol = 'blacktriangledown' if i == 0 else 'blacktriangle'
        ax.set_xlabel(f'$\\{symbol}_P$ (mm)')
        ax.set_xlim((0, 2500))
        ax.grid()
        ax.legend()
    show_or_save_plot(f'delta_p', show)


if __name__ == '__main__':
    b = True
    main_delta_p_distribution(fast=b, show=b)
