import os.path as op

from utils.utils_path.utils_path import OBSERVATION_PATH

#  Watershed options
watershed_name_to_color = {
    'Dargol_Kakassi': '#ffa500',
    'Sirba_GarbeKourou': '#0Bda51',
    'Gorouol_Alcongui': '#c4ceff',
    'Tapoa_CampementW': '#ffa940ff',
    'Nakanbe_Wayen': '#de3163',
    'Oueme_Beterou': '#aececfff',
    'Sota_Couberi': '#c57f7fff',
    'Pendjari_Porga': '#7f7fc5ff',
}

watershed_name_to_label = {
    'Dargol_Kakassi': 'Dargol',
    'Sirba_GarbeKourou': 'Sirba',
    'Gorouol_Alcongui': 'Gorouol',
    'Tapoa_CampementW': 'Tapoa',
    'Nakanbe_Wayen': 'Nakanbé',
    'Oueme_Beterou': 'Oueme',
    'Sota_Couberi': 'Sota',
    'Pendjari_Porga': 'Pendjari',
}

watershed_name_to_prefix = {
    'Oueme_Bonou': 'OUEME_BONOU',
    'Dargol_Kakassi': 'DARGOL_KAKASSI',
    'Sirba_GarbeKourou': 'SIRBA_GARBE_KOUROU',
    'Sota_Couberi': 'SOTA_COUBERI',
    'Gorouol_Alcongui': 'GOROUOL_ALCONGUI',
    'Tapoa_CampementW': 'TAPOA_W',
    'Pendjari_Porga': 'PENDJARI_PORGA',
    'Oueme_Beterou': 'OUEME_PONT_DE_BETEROU',
    'Nakanbe_Wayen': 'barrages_WAYEN',
}


def get_csv_filepath(watershed_name: str):
    assert watershed_name in watershed_name_to_prefix, f'file does not exist for {watershed_name} '
    prefix = watershed_name_to_prefix[watershed_name]
    return op.join(OBSERVATION_PATH, "Christophe2024", f"{prefix}_Rainfall_Runoff.csv")
