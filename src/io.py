import os
import geopandas as gpd
import pandas as pd

from csv import Sniffer
from config.config import settings


def read_egon_gpkgs():
    """ Reads eGo^n Geopackages. File directory and names have to be specified in settings.toml
    """
    directory = settings.data_path
    files = settings.egon_files

    gpkg_dict = {}

    for f in files:
        idx = f.split('.')[-2]
        gpkg_dict[idx] = gpd.read_file(os.path.join(directory, f))

    return gpkg_dict

def read_bast_data():
    """ Reads BAST data. File directory and names have to be specified in settings.toml
    """
    directory = settings.data_path
    files = settings.bast_files

    bast_dict = {}

    for f in files:
        idx = f.split('.')[0]
        bast_dict[idx] = pd.read_csv(os.path.join(directory, f), delimiter=";")

    return bast_dict