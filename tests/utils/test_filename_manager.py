from utils.utils_path.filename_manager.attribution_filename_manager import AttributionFilenameManager
from utils.utils_path.filename_manager.bifurcation_filename_manager import BifurcationFilenameManager
from utils.utils_path.filename_manager.calibration_filename_manager import CalibrationFilenameManager


def test_calibration_filename_manager():
    forcing_function_name = "f"
    observation_constraint_name = "o"
    manager = CalibrationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1999, 1, "v1", "RK45")
    assert manager == manager
    #  change obs_name
    other_manager = CalibrationFilenameManager(observation_constraint_name + "suffix", 10, forcing_function_name, 2,
                                               1999, 1, "v1", "RK45")
    assert manager != other_manager
    assert other_manager != manager
    #  change sample
    other_manager = CalibrationFilenameManager(observation_constraint_name, 100, forcing_function_name, 2, 1999, 1, "v1", "RK45")
    assert manager != other_manager
    assert other_manager != manager
    #  change forcing function name
    extended_forcing_function_name = forcing_function_name + "suffix"
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, extended_forcing_function_name, 2, 1999,
                                               1, "v1", "RK45")
    assert other_manager == manager
    assert manager != other_manager
    #  change ensemble size
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, forcing_function_name, 4, 1999, 1, "v1", "RK45")
    assert manager == other_manager
    assert other_manager != manager
    #  change initial year for loading (for the same forcing)
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 2000, 1, "v1", "RK45")
    assert manager != other_manager
    assert other_manager != manager
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1998, 1, "v1", "RK45")
    assert manager != other_manager
    assert other_manager != manager
    #  change initial year for loading (for an extended forcing)
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, extended_forcing_function_name, 2, 2000,
                                               1, "v1", "RK45")
    assert other_manager == manager
    assert manager != other_manager
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, extended_forcing_function_name, 2, 1999,
                                               1, "v1", "RK45")
    assert other_manager == manager
    assert manager != other_manager
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, extended_forcing_function_name, 2, 1998,
                                               1, "v1", "RK45")
    assert other_manager != manager
    assert manager != other_manager
    #  change nb years for initial state
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1999, 2, "v1", "RK45")
    assert manager != other_manager
    assert other_manager != manager
    #  change nb years for initial state
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1999, 1, "v2", "RK45")
    assert manager != other_manager
    assert other_manager != manager
    #  change method solver
    other_manager = CalibrationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1999, 1, "v2", "RK23")
    assert manager != other_manager
    assert other_manager != manager


def test_bifurcation_filename_manager():
    forcing_function_name = "f"
    observation_constraint_name = "o"
    manager = BifurcationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1999, 1, "v1", "RK45",
                                         min_forcing=1.0, max_forcing=2.0)
    other = BifurcationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1999, 1, "v1", "RK45",
                                       min_forcing=1.0, max_forcing=4.0)
    assert other != manager
    other = BifurcationFilenameManager(observation_constraint_name, 10, forcing_function_name, 4, 1999, 1, "v1", "RK45",
                                       min_forcing=1.0,
                                       max_forcing=2.0)
    assert manager == other
    other = BifurcationFilenameManager(observation_constraint_name, 10, forcing_function_name, 4, 1999, 1, "v1", "RK45",
                                       min_forcing=1.0,
                                       max_forcing=2.0)
    assert manager == other
    assert other != manager
    suffix = '_suffix'
    other = BifurcationFilenameManager(observation_constraint_name, 10, forcing_function_name + suffix, 2, 1999, 1,
                                       "v1", "RK45",
                                       min_forcing=1.0, max_forcing=2.0)
    assert manager != other
    assert other == manager
    other = BifurcationFilenameManager(observation_constraint_name, 10, suffix, 2, 1999, 1, "v1", "RK45",
                                       min_forcing=1.0,
                                       max_forcing=2.0)
    assert other != manager
    assert manager != other
    other = BifurcationFilenameManager(observation_constraint_name, 10, forcing_function_name, 2, 1999, 2, "v1", "RK45",
                                       min_forcing=1.0, max_forcing=2.0)
    assert other != manager
    assert manager != other


# def test_attribution_filename_manager():
#     manager = AttributionFilenameManager("o", 10, 'f', 2, 1999, 1, 1., 2., "n", 1990, 1999)
#     assert manager == manager
#     other_manager = AttributionFilenameManager("o suffix", 10, 'f', 2, 1999, 1, 1., 2., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 100, 'f', 2, 1999, 1, 1., 2., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f_suffix', 2, 1999, 1, 1., 2., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 4, 1999, 1, 1., 2., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 2000, 1, 1., 2., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 1999, 1, 0., 2., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 1999, 1, 1., 3., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 1999, 1, 1., 2., "n2", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 1999, 1, 1., 2., "n", 1991, 1999)
#     assert other_manager == manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 1999, 1, 1., 2., "n", 1990, 1998)
#     assert other_manager == manager
#     assert manager != other_manager
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 1999, 2, 1., 2., "n", 1990, 1999)
#     assert other_manager != manager
#     assert manager != other_manager
#     #  Final check for a special case
#     manager = AttributionFilenameManager("o", 10, 'f', 2, 1990, 1, 1., 2., "n", 1990, 1999)
#     other_manager = AttributionFilenameManager("o", 10, 'f', 2, 1990, 1, 1., 2., "n", 1996, 1998)
#     assert other_manager == manager
#     assert manager != other_manager
