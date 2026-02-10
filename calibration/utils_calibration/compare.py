import os
import os.path as op

import pandas as pd

from utils.utils_path.utils_path import CALIBRATION_DATA_PATH

"""Compare different version of the calibration code for the 8 tiphyc watersheds"""
def calibration_comparison():
    path = op.join(CALIBRATION_DATA_PATH, 'TiphycAnnual')
    d = {}
    for folder in os.listdir(path):
        if '1000000' in folder:
            folder_path = op.join(path, folder)
            files = os.listdir(folder_path)
            if len(files) == 8:
                s = pd.Series({file[:-4]: pd.read_csv(op.join(folder_path, file), index_col=0)['Error'].mean()
                            for file in sorted(files)})
                d[folder] = s
    df = pd.DataFrame(d).transpose()
    df['Mean'] = df.mean(axis=1)
    print(df.to_string())

if __name__ == '__main__':
    calibration_comparison()