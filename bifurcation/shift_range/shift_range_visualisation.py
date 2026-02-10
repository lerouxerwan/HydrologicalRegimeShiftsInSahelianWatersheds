from matplotlib import pyplot as plt

from bifurcation.shift_range.shift_range import ShiftRange


def plot_shift_range_marker(ax, shift_range, size=100, color='k', add_label=False, suffix='', i=None):
    if shift_range.branches_are_crossing:
        shift_range = InverseShiftRangeForPlots.from_shift_range(shift_range)
    for j, (shift_forcing, shift_state) in enumerate(zip(*shift_range.original_data_structure)):
        plot = True if i is None else j == i
        if plot:
            marker = '^' if j == 0 else 'v'
            #  Add marker for the end of each branch
            if add_label:
                label = f"{'highest' if j == 0 else 'lowest'} attractor of the {'lower' if j == 0 else 'upper'} branch"
                if suffix:
                    label = f'Average {label} for {suffix}'
            else:
                label = None
            ax.scatter(shift_forcing, shift_state, marker=marker, color=color, s=size, label=label)


def plot_ticks_shift_range(ax, shift_range: ShiftRange, size = 10):
    # Package for ticks
    # plt.rcParams.update()["text.latex.preamble"].join([
    #     r"\usepackage{dashbox}",
    #     r"\setmainfont{xcolor}",
    #     r'\usepackage{amssymb}'
    # ])
    plt.rc('text.latex', preamble=r'\usepackage{amssymb}')
    # Set ticks
    minor_x_labels = [f'$\\{symbol}_P$' for symbol in ['blacktriangle', 'blacktriangledown']]
    ax_twinx = ax.twiny()
    ax_twinx.set_xlim(ax.get_xlim())
    minor_xticks = (shift_range.forcing_lower_state, shift_range.forcing_upper_state)
    ax_twinx.set_xticks(minor_xticks, labels=minor_x_labels)
    ax_twinx.tick_params(axis='x', which='major', labelsize=size)
    # Yticks
    minor_y_labels = [f'$\\{symbol}_S$' for symbol in ['blacktriangle', 'diamondsuit', 'blacktriangledown']]
    minor_y_ticks = (shift_range.lower_state_value, shift_range.middle_state_value, shift_range.upper_state_value)
    ax_twiny = ax.twinx()
    ax_twiny.set_ylim(ax.get_ylim())
    ax_twiny.set_yticks(minor_y_ticks, labels=minor_y_labels)
    ax_twiny.tick_params(axis='y', which='major', labelsize=size)



class InverseShiftRangeForPlots(ShiftRange):

    def __post_init__(self):
        """Ignore previous checks"""
        pass

    @classmethod
    def from_shift_range(cls, shift_range: ShiftRange):
        return cls(lower_state_value=shift_range.upper_state_value,
                   upper_state_value=shift_range.lower_state_value,
                   forcing_lower_state=shift_range.forcing_upper_state,
                   forcing_upper_state=shift_range.forcing_lower_state)
