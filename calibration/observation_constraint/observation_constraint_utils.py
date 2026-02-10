import pandas as pd


def load_csv_with_constraint(column_index, constraint_name, filepath):
    # Load data from the file
    s = load_series(column_index, filepath)
    years = [int(t) for t in s.index]
    states = s.values
    return years, {constraint_name: states}


def load_series(column_index, filepath):
    df = pd.read_csv(filepath, sep=",", header=0, index_col=0)
    s = df.iloc[:, column_index]
    s = s.loc[~s.isnull()]
    return s


#  In the *fcover_all.csv files, the vegetation is available for the entire year and correspond to the NDVI
#  the vegetation is always extracted for the largest contour fo the watershed
#  for the place 'KoriDantiandou' we have the vegetation but not the runoff because it is an Endorheic basin
watershed_name_to_filename_for_satellite_vegetation = {
    'Dargol_Kakassi': 'Dargol_fcover_all.csv',
    'Oueme_Beterou': 'Beterou_fcover_all.csv',
    'Gorouol_Alcongui': 'Gorouol_fcover.csv',
    'Tapoa_CampementW': 'Tapoa_fcover_all.csv',
    'KoriDantiandou': 'Kori_fcover_all.csv',
    'Pendjari_Porga': 'Pendjari_fcover_all.csv',
    'Sirba_GarbeKourou': 'Sirba_fcover_all.csv',
    'Oueme_Bonou': 'Oueme_fcover_all.csv',
}
