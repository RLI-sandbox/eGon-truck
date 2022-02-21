from __future__ import annotations

import logging

from geopandas import GeoDataFrame

from egon_truck.config.config import settings
from egon_truck.data_io import get_germany_gdf
from egon_truck.geo import geo_intersect, voronoi

log = logging.getLogger(__name__)


def calculate_total_hydrogen_consumption(scenario: str = "nep_scenario"):
    """Calculate the total hydrogen demand for trucking in Germany"""
    leakage = settings["constants"].leakage
    leakage_rate = settings["constants"].leakage_rate
    hgv_mileage = settings[scenario].hgv_mileage  # km
    hydrogen_consumption = settings["constants"].hydrogen_consumption  # kg/100km
    fcev_share = settings["constants"].fcev_share

    hydrogen_consumption_per_km = hydrogen_consumption / 100  # kg/km

    # calculate total hydrogen consumption kg/a
    if leakage:
        return (
            hgv_mileage * hydrogen_consumption_per_km * fcev_share / (1 - leakage_rate)
        )
    else:
        return hgv_mileage * hydrogen_consumption_per_km * fcev_share


def blunt_hydrogen_consumption(
    truck_data: GeoDataFrame,
    scenario: str = "nep_scenario",
):
    """
    Maps hydrogen consumption to the MV Grid Districts in a blunt and direct matter.
    """
    relevant_columns = settings["data"].relevant_columns

    total_hydrogen_consumption = calculate_total_hydrogen_consumption(scenario=scenario)

    # distribute consumption
    traffic_volume = truck_data.groupby(by="mv_grid_district").agg(
        {relevant_columns[0]: sum}
    )

    normalized_traffic_volume = (
        traffic_volume[relevant_columns[0]] / traffic_volume[relevant_columns[0]].sum()
    )

    return normalized_traffic_volume * total_hydrogen_consumption


def voronoi_hydrogen_consumption(
    truck_data: GeoDataFrame,
    grid_districts: GeoDataFrame,
    scenario: str = "nep_scenario",
):
    """
    Maps hydrogen consumption to the MV Grid Districts by building a Voronoi Field.
    """
    # get german borders
    gdf = get_germany_gdf()

    # drop points outside germany and nan values
    truck_data_within = truck_data.dropna().loc[truck_data.within(gdf.geometry.iat[0])]

    voronoi_gdf = voronoi(truck_data_within, gdf)

    grid_districts = geo_intersect(voronoi_gdf, grid_districts)

    total_hydrogen_consumption = calculate_total_hydrogen_consumption(scenario=scenario)

    grid_districts = grid_districts.assign(
        normalized_truck_traffic=grid_districts.truck_traffic
        / grid_districts.truck_traffic.sum()
    )

    grid_districts = grid_districts.assign(
        hydrogen_consumption=(
            grid_districts.normalized_truck_traffic * total_hydrogen_consumption
        )
    )

    return grid_districts
