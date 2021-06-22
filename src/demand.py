import logging

from .io import get_germany_gdf
from .geo import voronoi, geo_intersect
from config.config import settings

log = logging.getLogger(__name__)


def calculate_total_hydrogen_consumption(leakage=True):
    """ Calculate the total hydrogen demand for trucking in Germany
    """
    leakage_rate = settings.leakage_rate
    hgv_amount = settings.hgv_amount
    hgv_mean_mileage = settings.hgv_mean_mileage  # km/a
    hydrogen_consumption = settings.hydrogen_consumption  # kg/100km

    hydrogen_consumption_per_km = hydrogen_consumption / 100  # kg/km

    # calculate total hydrogen consumption kg/a
    if leakage:
        return hgv_amount * hgv_mean_mileage * hydrogen_consumption_per_km / (1-leakage_rate)
    else:
        return hgv_amount * hgv_mean_mileage * hydrogen_consumption_per_km


def blunt_hydrogen_consumption(truck_data):
    """ Maps hydrogen consumption to the MV Grid Districts in a blunt and direct matter.
    """
    relevant_columns = settings.relevant_columns

    total_hydrogen_consumption = calculate_total_hydrogen_consumption()

    # distribute consumption
    traffic_volume = truck_data.groupby(by="mv_grid_district").agg({relevant_columns[0]: sum})

    normalized_traffic_volume = traffic_volume[relevant_columns[0]] / traffic_volume[relevant_columns[0]].sum()

    hydrogen_consumption = normalized_traffic_volume * total_hydrogen_consumption

    return hydrogen_consumption


def voronoi_hydrogen_consumption(truck_data, grid_districts):
    """ Maps hydrogen consumption to the MV Grid Districts by building a Voronoi Field.
    """
    # get german borders
    gdf = get_germany_gdf()

    # drop points outside germany and nan values
    truck_data_within = truck_data.dropna().loc[truck_data.within(gdf.geometry.iat[0])]

    voronoi_gdf = voronoi(truck_data_within, gdf)

    grid_districts = geo_intersect(voronoi_gdf, grid_districts)

    total_hydrogen_consumption = calculate_total_hydrogen_consumption()

    grid_districts = grid_districts.assign(
        normalized_truck_traffic=grid_districts.truck_traffic / grid_districts.truck_traffic.sum())

    grid_districts = grid_districts.assign(
        hydrogen_consumption=grid_districts.normalized_truck_traffic * total_hydrogen_consumption)

    return grid_districts
