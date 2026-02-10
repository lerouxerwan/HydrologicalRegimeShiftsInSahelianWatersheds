import copy

from matplotlib import pyplot as plt

from bifurcation.bifurcation import Bifurcation
from bifurcation.bifurcation_data.bifurcation_data import BifurcationData
from projects.paper_model.section_7_appendix.utils_compute_is_bistable import compute_is_bistable_wrt_to_some_forcing, \
    compute_percentage_bistable
from projects.paper_model.utils_paper_model import get_calibration
from utils.utils_plot import show_or_save_plot
from utils.utils_watershed import watershed_name_to_color, watershed_name_to_label

monostable_ensemble_ids =     [4, 17, 18, 23, 24, 30, 33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 47, 49, 52, 56, 60, 61, 62, 63, 65, 66, 67, 68,
     70, 71, 72, 74, 77, 78, 81, 82, 84, 86, 89, 91, 92, 94, 95, 102, 104, 105, 107, 109, 110, 111, 112, 113, 114, 115,
     117, 122, 124, 125, 126, 130, 132, 137, 140, 141, 142, 143, 145, 146, 150, 151, 152, 157, 158, 159, 160, 161, 163,
     164, 166, 167, 169, 172, 177, 178, 179, 180, 181, 182, 183, 184, 187, 188, 189, 193, 194, 195, 197, 200, 201, 202,
     204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 216, 217, 219, 221, 222, 225, 226, 227, 228, 229, 230, 231,
     232, 236, 237, 240, 242, 246, 250, 251, 252, 253, 256, 258, 260, 263, 266, 269, 272, 273, 277, 278, 280, 281, 283,
     285, 287, 288, 290, 291, 293, 294, 295, 299, 300, 303, 305, 306, 307, 308, 311, 312, 313, 316, 317, 318, 319, 320,
     323, 324, 326, 327, 329, 333, 334, 335, 336, 337, 341, 343, 344, 345, 347, 350, 352, 354, 356, 357, 360, 361, 364,
     365, 374, 377, 380, 383, 385, 386, 387, 390, 391, 392, 394, 396, 400, 403, 406, 408, 411, 412, 413, 414, 416, 419,
     421, 425, 427, 428, 429, 430, 432, 433, 434, 436, 439, 441, 442, 444, 445, 449, 450, 451, 453, 454, 460, 464, 465,
     466, 468, 470, 474, 475, 479, 480, 483, 484, 488, 489, 492, 494, 496, 497, 500, 501, 502, 503, 504, 506, 507, 509,
     510, 512, 513, 514, 518, 525, 530, 531, 532, 533, 534, 535, 536, 540, 542, 545, 546, 548, 549, 550, 551, 556, 557,
     560, 566, 569, 570, 577, 579, 580, 581, 585, 587, 589, 594, 596, 600, 602, 608, 610, 612, 615, 623, 624, 626, 627,
     629, 633, 635, 636, 637, 641, 643, 648, 650, 654, 660, 665, 667, 672, 675, 679, 681, 682, 685, 687, 689, 692, 693,
     695, 698, 700, 701, 702, 708, 709, 713, 714, 715, 716, 721, 728, 730, 733, 739, 740, 741, 746, 748, 749, 751, 753,
     754, 757, 758, 761, 766, 767, 768, 772, 773, 777, 778, 781, 787, 789, 791, 792, 793, 798, 799, 802, 803, 804, 806,
     810, 811, 812, 814, 817, 820, 822, 823, 824, 825, 826, 832, 834, 838, 842, 844, 845, 851, 852, 854, 856, 858, 863,
     865, 866, 869, 873, 875, 877, 879, 881, 883, 885, 887, 888, 890, 893, 895, 901, 903, 905, 914, 918, 919, 924, 925,
     931, 938, 939, 944, 946, 951, 952, 961, 965, 967, 971, 972, 974, 982, 984, 986, 990, 994, 995, 997]

def main_sensitivity_monostable_nakanbe(fast: bool, show: bool):
    ax = plt.gca()
    watershed_name = 'Nakanbe_Wayen'
    color = watershed_name_to_color[watershed_name]
    label = watershed_name_to_label[watershed_name]
    calibration = get_calibration(watershed_name, fast)
    bifurcation = Bifurcation(calibration, max_forcing=4000., ensemble_ids=monostable_ensemble_ids)
    print(len(bifurcation.ensemble_id_to_bifurcation_data))
    max_forcing_list = list(range(0, 4000))[::10]
    percentage_bistable = [compute_percentage_bistable(bifurcation, float(forcing)) for forcing in max_forcing_list]


    ax.plot(max_forcing_list, percentage_bistable, color=color, label=label)
    ax.set_xlabel('Maximum precipitation level to check bistability (mm)')
    ax.set_ylabel('Percentage of bistable ensemble members (%)')
    ax.set_xlim((max_forcing_list[0], max_forcing_list[-1]))
    ax.set_ylim((-10, 110))
    ax.legend()
    show_or_save_plot(f'sensitivity_monostable_nakanbe', show)




if __name__ == '__main__':
    b = False
    main_sensitivity_monostable_nakanbe(b, b)