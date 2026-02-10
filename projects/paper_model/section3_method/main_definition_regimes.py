import numpy as np
from matplotlib import pyplot as plt

from bifurcation.bifurcation import Bifurcation
from bifurcation.bifurcation_visualisation import _plot_bifurcation_graph, _plot_shift_range, \
    add_bifurcation_labels
from projects.paper_model.utils_paper_model import get_calibration
from utils.utils_plot import show_or_save_plot, subplots_custom


def plot_monostable_bifurcation_diagram(fast=False, show=False):
    watershed_name, limit1, limit2 = 'Nakanbe_Wayen', 1., 4000.
    calibration = get_calibration(watershed_name, fast=fast)
    bifurcation = Bifurcation(calibration)
    variable_name = 'c'



    for ensemble_id in bifurcation.monostable_ensemble_ids:
        ax = plt.gca()
        forcings = np.arange(limit1, stop=limit2 + 1)
        bifurcation_data = bifurcation.ensemble_id_to_bifurcation_data[ensemble_id]
        _plot_bifurcation_graph(calibration, ax, variable_name, forcings, ensemble_id, bifurcation_data)
        ax.grid()
        add_bifurcation_labels(ax, calibration, variable_name)
        ax.set_ylim((0, 1))
        ax.set_xlim((limit1, limit2))
        show_or_save_plot(f'regimes_{ensemble_id}', show)


def plot_definition_regimes_with_two_bifurcation_diagrams(fast=False, show=False):
    fig, axs = subplots_custom(1, 2)
    limit1, limit2 = 1., 4000.
    l = [
        ('Nakanbe_Wayen', 36),
        ('Dargol_Kakassi', 0),
    ]

    variable_name = 'c'
    print(len(l))
    for j, (watershed_name, ensemble_id) in enumerate(l):
        ax = axs[j]
        calibration = get_calibration(watershed_name, fast=fast)
        calibration.show = show
        bifurcation = Bifurcation(calibration)
        bifurcation_data = bifurcation.ensemble_id_to_bifurcation_data[ensemble_id]
        # Plot part
        forcings = np.arange(limit1, stop=limit2 + 1)
        _plot_bifurcation_graph(calibration, ax, variable_name, forcings, ensemble_id, bifurcation_data)

        ax.grid()
        add_bifurcation_labels(ax, calibration, variable_name)
        ax.set_ylim((0, 1))
        ax.set_xlim((limit1, limit2))

    for letter, ax in zip('ab', axs):
        ymin, ymax = ax.get_ylim()
        y_text = ymin + 0.9 * (ymax - ymin)
        xmin, xmax = ax.get_xlim()
        x_text = xmin + 0.9 * (xmax - xmin)
        ax.text(x_text, y_text, f'({letter})', weight="bold", fontsize=10)

    show_or_save_plot("bifurcation_diagrams", show)


def plot_definition_two_regimes(fast=False, show=False):
    fig, axs = subplots_custom(1, 2)
    limit1, limit2 = 1., 2000.
    watershed_name, ensemble_id = 'Dargol_Kakassi', 0
    variable_name = 'c'

    for j in range(2):
        ax = axs[j]
        ax.set_ylim((0, 1))
        calibration = get_calibration(watershed_name, fast=fast)
        calibration.show = show
        bifurcation = Bifurcation(calibration)
        bifurcation_data = bifurcation.ensemble_id_to_bifurcation_data[ensemble_id]
        # Plot part
        forcings = np.arange(limit1, stop=limit2 + 1)
        _plot_bifurcation_graph(calibration, ax, variable_name, forcings, ensemble_id, bifurcation_data)
        _plot_shift_range(ax, bifurcation_data, forcings, calibration, variable_name, ensemble_id, j)

        ax.grid()
        add_bifurcation_labels(ax, calibration, variable_name)
        ax.set_xlim((limit1, limit2))

    for letter, ax in zip('ab', axs):
        ymin, ymax = ax.get_ylim()
        y_text = ymin + 0.9 * (ymax - ymin)
        xmin, xmax = ax.get_xlim()
        x_text = xmin + 0.9 * (xmax - xmin)
        ax.text(x_text, y_text, f'({letter})', weight="bold", fontsize=10)

    show_or_save_plot("regimes", show)


if __name__ == '__main__':
    # plot_monostable_bifurcation_diagram(False, False)
    # plot_definition_regimes_with_two_bifurcation_diagrams(fast=False, show=False)
    plot_definition_two_regimes(False, False)