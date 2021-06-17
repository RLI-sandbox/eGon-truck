import os
import pandas as pd
import geopandas as gpd

from config.config import settings


def read_egon_gpkgs():
    """ Reads eGo^n Geopackages. File directory and names have to be specified in settings.toml
    """
    directory = settings.data_path
    files = settings.egon_files
    epsg = settings.egon_epsg

    gpkg_dict = {}

    for f in files:
        idx = f.split('.')[-2]
        gpkg_dict[idx] = gpd.read_file(os.path.join(directory, f)).set_crs(
            epsg=epsg, inplace=True
        )

    return gpkg_dict

def read_bast_data():
    """ Reads BAST data. File directory and names have to be specified in settings.toml
    """
    directory = settings.data_path
    file = settings.bast_file
    relevant_columns = settings.relevant_columns
    init_epsg = settings.bast_epsg
    final_epsg = settings.egon_epsg

    bast_dict = {}

    name = file.split('.')[0]
    bast_dict[name] = pd.read_csv(
        os.path.join(directory, file), delimiter=";", decimal=",", index_col=[0])

    relevant_df = bast_dict[name][relevant_columns].copy()

    relevant_df[relevant_columns[0]] = relevant_df[relevant_columns[0]].astype(float)

    name = "truck_data"

    bast_dict[name] = gpd.GeoDataFrame(
        relevant_df[relevant_columns[0]], geometry=gpd.points_from_xy(
            relevant_df[relevant_columns[1]], relevant_df[relevant_columns[2]])).set_crs(
        epsg=init_epsg, inplace=True
    ).to_crs(epsg=final_epsg)

    return bast_dict