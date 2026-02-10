from bifurcation.bifurcation import Bifurcation
from projects.paper_model.utils_paper_model import get_calibration


def main_bifurcation():
    watershed_name = ['Gorouol_Alcongui', 'Dargol_Kakassi', 'Sirba_GarbeKourou', 'Nakanbe_Wayen'][3]
    calibration = get_calibration(watershed_name, False)
    bifurcation = Bifurcation(calibration, max_forcing=4000.)
    print(bifurcation.bifurcation_data_list)

if __name__ == '__main__':
    main_bifurcation()