from continuation.get_continuation_bifurcation_attributes import get_bifurcation_attributes
from continuation.get_continuation_interpolated import get_continuation_interpolated


def main_get_attractors_and_repulsors():
    # General parameters
    min_forcing = 1.
    max_forcing = 2000.
    # Main loop
    watershed_name = ['Gorouol_Alcongui', 'Dargol_Kakassi', 'Sirba_GarbeKourou', 'Nakanbe_Wayen'][1]
    print(watershed_name)
    get_bifurcation_attributes(watershed_name, 0, min_forcing, max_forcing)

if __name__ == '__main__':
    main_get_attractors_and_repulsors()
