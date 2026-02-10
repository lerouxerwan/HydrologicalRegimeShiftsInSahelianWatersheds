import sys

from continuation.get_continuation import get_continuation_parallel


def main_get_continuation():
    if len(sys.argv) > 1:
        index = int(sys.argv[1])
    else:
        index = 1
    print(f'Run with index={index}')

    # General parameters
    min_forcing = 1.
    max_forcing = 4000.
    ensemble_ids = list(range(324, 613))[::1]
    # Main loop
    watershed_name = ['Gorouol_Alcongui', 'Dargol_Kakassi', 'Sirba_GarbeKourou', 'Nakanbe_Wayen'][index]
    print(watershed_name)
    get_continuation_parallel(watershed_name, ensemble_ids, min_forcing, max_forcing, parallel=False)

if __name__ == '__main__':
    main_get_continuation()
