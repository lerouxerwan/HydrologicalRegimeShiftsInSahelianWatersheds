import os
import os.path as op

#  Path to root folder
ROOT = op.dirname(op.dirname(op.dirname(os.path.abspath(__file__))))

# Path to the current directory
CURRENT_PATH = os.getcwd()

#  Data parameters
DATA_PATH = op.join(ROOT, 'data')
RAW_DATA_PATH = op.join(DATA_PATH, 'raw')
EXTRACTED_DATA_PATH = op.join(DATA_PATH, 'extracted')
PROVIDED_DATA_PATH = op.join(DATA_PATH, 'provided')
OBSERVATION_PATH = op.join(PROVIDED_DATA_PATH, 'observations')
CALIBRATION_DATA_PATH = op.join(DATA_PATH, 'calibration')
BIFURCATION_DATA_PATH = op.join(DATA_PATH, 'bifurcation')
ATTRIBUTION_DATA_PATH = op.join(DATA_PATH, 'attribution')
EMULATION_DATA_PATH = op.join(DATA_PATH, 'emulation')
DATASET_DATA_PATH = op.join(DATA_PATH, 'dataset')
CONTINUATION_DATA_PATH = op.join(DATA_PATH, 'continuation')
CONTINUATION_INTERPOLATED_DATA_PATH = op.join(DATA_PATH, 'continuation_interpolated')
CONTINUATION_BIFURCATION_DATA_PATH = op.join(DATA_PATH, 'continuation_bifurcation')


#  Result parameters
RESULT_PATH = op.join(ROOT, 'results')


