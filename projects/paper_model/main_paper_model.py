from projects.paper_model.section2_data.main_obs_data import plot_data
from projects.paper_model.section3_method.main_definition_regimes import \
    plot_definition_regimes_with_two_bifurcation_diagrams
from projects.paper_model.section4_results.subsection1_calibration.main_delta_p_distribution_2d import \
    main_delta_p_distribution_2d
from projects.paper_model.section4_results.subsection1_calibration.main_trajectory import main_plot_trajectory
from projects.paper_model.section4_results.subsection2_regime_shift_with_obs.main_percentage_along_time_together import \
    main_plot_percentage_lower_area
from projects.paper_model.section_7_appendix.main_more_metrics import main_more_metrics
from projects.paper_model.section_7_appendix.main_sensitivity_max_forcing import main_plot_sensitivity_max_forcing


def main_paper_plot(fast, show):
    # Data and method
    plot_functions = [plot_data, plot_definition_regimes_with_two_bifurcation_diagrams]
    # Results - section 1
    plot_functions += [main_plot_trajectory]
    # Results - section 2
    plot_functions += [main_delta_p_distribution_2d]
    # Results - section 3
    plot_functions += [main_plot_percentage_lower_area]
    # Results - appendix
    plot_functions += [main_plot_sensitivity_max_forcing, main_more_metrics]
    # Loop to generate all the plots
    for plot_function in plot_functions:
        plot_function(fast, show)


if __name__ == '__main__':
    b = False
    main_paper_plot(False, False)
