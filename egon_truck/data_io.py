from __future__ import annotations

import logging

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from egon_truck.config.config import settings

log = logging.getLogger(__name__)


def read_egon_gpkgs():
    """
    Reads eGo^n Geopackages. File directory and names have to be specified in
    settings.toml
    """
    log.info("Read eGo^n data.")

    directory = Path(settings["data"].data_path).resolve()
    files = settings["data"].egon_files
    epsg = settings["data"].egon_epsg

    gpkg_dict = {}

    for f in files:
        idx = f.split(".")[-2]
        gpkg_dict[idx] = gpd.read_file(directory / f).set_crs(epsg=epsg, inplace=True)

    log.info("Done.")

    return gpkg_dict


def read_bast_data():
    """
    Reads BAST data. File directory and names have to be specified in settings.toml
    """
    log.info("Read BAST data.")

    directory = Path(settings["data"].data_path).resolve()
    file = settings["data"].bast_file
    relevant_columns = settings["data"].relevant_columns
    init_epsg = settings["data"].bast_epsg
    final_epsg = settings["data"].egon_epsg

    bast_dict = {}

    name = file.split(".")[0]
    bast_dict[name] = pd.read_csv(
        directory / file,
        delimiter=r";",
        decimal=r",",
        thousands=r".",
        encoding="ISO-8859-1",
    )

    relevant_df = bast_dict[name][relevant_columns].copy()  # type: pd.DataFrame

    relevant_df[relevant_columns[0]] = relevant_df[relevant_columns[0]].astype(float)

    name = "truck_data"

    bast_dict[name] = (
        gpd.GeoDataFrame(
            relevant_df[relevant_columns[0]],
            geometry=gpd.points_from_xy(
                relevant_df[relevant_columns[1]], relevant_df[relevant_columns[2]]
            ),
        )
        .set_crs(epsg=init_epsg, inplace=True)
        .to_crs(epsg=final_epsg)
    )

    log.info("Done.")

    return bast_dict


def get_germany_gdf():
    """
    Read in German Border from geo.json file. File directory and names have to be
    specified in settings.toml
    """
    log.info("Read Germany GeoJSON.")

    directory = Path(settings["data"].data_path).resolve()
    json = settings["data"].germany_json
    init_epsg = settings["data"].germany_epsg
    final_epsg = settings["data"].egon_epsg

    gdf = (
        gpd.read_file(directory / json)
        .set_crs(epsg=init_epsg, inplace=True)
        .to_crs(epsg=final_epsg)
    )

    log.info("Done.")

    return gdf


def export_results(
    hydrogen_consumption: gpd.GeoDataFrame,
    mode: str,
    scenario: str = "nep_scenario",
) -> object:
    """Export results as CSV and generate a Plot."""
    log.info(f"Export {mode} results for scenario {scenario}.")

    output_dir = Path(settings["results"].output_dir).resolve()
    output_csv = settings["results"].output_csv
    output_png = settings["results"].output_png

    output_dir.mkdir(parents=True, exist_ok=True)

    hydrogen_consumption.to_csv(output_dir / output_csv.format(mode, scenario))

    hydrogen_consumption = hydrogen_consumption.assign(
        hydrogen_consumption_in_t=hydrogen_consumption.hydrogen_consumption / 1000
    )

    hydrogen_consumption.plot(
        column="hydrogen_consumption_in_t",
        legend=True,
        legend_kwds={"label": r"Hydrogen Consumption in t/a"},
    )

    plt.axis("off")

    plt.savefig(
        output_dir / output_png.format(mode, scenario), dpi=300, bbox_inches="tight"
    )

    plt.close()

    log.info("Done.")
