from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from bifurcation.bifurcation_visualisation import add_bifurcation_labels
from projects.paper_model.section4_results.subsection1_calibration.utils_distribution import \
    get_watershed_name_to_shift_range_list
from utils.utils_plot import show_or_save_plot, subplots_custom
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label


def main_delta_p_distribution_2d(fast=False, show=False):
    fig, axs = subplots_custom(2, 2)
    axs = axs.flatten()
    watershed_name_to_shift_range_list, watershed_name_to_bifurcation, watershed_name_to_annual_precipitation_values = get_watershed_name_to_shift_range_list(fast)
    for j, (watershed_name, shift_range_list) in enumerate(watershed_name_to_shift_range_list.items()):
        ax = axs[j]
        color_watershed = watershed_name_to_color[watershed_name]

        # Plot the climatology of the watershed for the same period
        annual_precipitation_values = watershed_name_to_annual_precipitation_values[watershed_name]
        color_box_plot = "k"
        ax.boxplot([annual_precipitation_values], positions=[0.43], vert=False, widths=0.05, whis=(0, 100),
                   patch_artist=True,
                   boxprops=dict(facecolor=color_watershed, color=color_box_plot),
                    capprops=dict(color=color_box_plot),
                    whiskerprops=dict(color=color_box_plot),
                    flierprops=dict(color=color_box_plot,
                    markeredgecolor=color_box_plot),
                    medianprops=dict(color=color_box_plot))

        # Plot lowest/highest attractors of the upper/lower branch
        for i, marker in enumerate(['^', 'v']):
            # ax = axs[i]
            if i == 0:
                color = 'grey'
                # points = [(s.forcing_lower_state, s.lower_state_value) for s in shift_range_list]
                x = [s.forcing_lower_state for s in shift_range_list]
                y = [s.lower_state_value for s in shift_range_list]
            else:
                color = 'k'
                x = [s.forcing_upper_state for s in shift_range_list]
                y = [s.upper_state_value for s in shift_range_list]
                # points = [(s.forcing_upper_state, s.upper_state_value) for s in shift_range_list]
            ax.scatter(x, y, color=color, marker=marker, s=10)

        # Set limits and labels
        ax.text(100, 0.03, f'({"abcd"[j]})', weight="bold", fontsize=10)
        bifurcation = watershed_name_to_bifurcation[watershed_name]
        add_bifurcation_labels(ax, calibration=bifurcation.calibration)
        ax.set_xlim(0, bifurcation.max_forcing)
        ymin, ymax = 0., 0.6
        ax.set_ylim(ymin, ymax)
        yticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        ax.set_yticks(yticks)
        ax.set_yticks(yticks)
        ax.set_yticklabels([str(ytick) for ytick in yticks])
        ax.grid()
        # Create custom legend
        color = watershed_name_to_color[watershed_name]
        watershed_label = watershed_name_to_label[watershed_name]
        legend_labels = [f"{'highest' if j == 0 else 'lowest'} attractor of the {'lower' if j == 0 else 'upper'} branch for {watershed_label}" for j in [1, 0]]
        legend_handles = [Line2D([], [], color='k' if j == 0 else 'grey', marker='^' if j == 1 else 'v', label="Observations", linestyle='None') for j in [0, 1]]
        # Add legend for the box plot
        legend_labels += [f'Box plot of annual precipitation for {watershed_label}']
        legend_handles += [Patch(facecolor=color_watershed, edgecolor='k')]
        ax.legend(handles=legend_handles, labels=legend_labels, loc="upper left")

    show_or_save_plot(f'delta_p', show)


if __name__ == '__main__':
    b = True
    main_delta_p_distribution_2d(fast=b, show=b)
