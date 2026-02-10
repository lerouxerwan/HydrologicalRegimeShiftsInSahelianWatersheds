from continuation.get_continuation_interpolated import get_continuation_interpolated


def main_get_continuation_interpolated():
    # General parameters
    min_forcing = 1.
    max_forcing = 2000.
    ensemble_ids = [0]
    # ensemble_ids = [0, 1, 2, 3]
    # Main loop
    watershed_name = ['Gorouol_Alcongui', 'Dargol_Kakassi', 'Sirba_GarbeKourou', 'Nakanbe_Wayen'][0]
    print(watershed_name)
    get_continuation_interpolated(watershed_name, ensemble_ids, min_forcing, max_forcing)

if __name__ == '__main__':
    main_get_continuation_interpolated()
