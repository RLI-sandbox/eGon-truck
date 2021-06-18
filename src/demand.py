from .io import get_germany_gdf
from .geo import voronoi
from config.config import settings


def calculate_total_hydrogen_consumption():
    """
    """
    hgv_amount = settings.hgv_amount
    hgv_mean_mileage = settings.hgv_mean_mileage  # km/a
    hydrogen_consumption = settings.hydrogen_consumption  # kg/100km

    hydrogen_consumption_per_km = hydrogen_consumption / 100  # kg/km

    # calculate total hydrogen consumption
    return hgv_amount * hgv_mean_mileage * hydrogen_consumption_per_km  # kg/a

def blunt_hydrogen_consumption(truck_data):
    """ Maps hydrogen consumption to the MV Grid Districts in a blunt and direct matter.
    """
    relevant_columns = settings.relevant_columns

    total_hydrogen_consumption = calculate_total_hydrogen_consumption()

    # distribute consumption
    traffic_volume = truck_data.groupby(by="mv_grid_district").agg({relevant_columns[0]: sum})

    normalized_traffic_volume = traffic_volume.DTV_SV_MobisSo_Q / traffic_volume.DTV_SV_MobisSo_Q.sum()

    hydrogen_consumption = normalized_traffic_volume*total_hydrogen_consumption

    return hydrogen_consumption

def voronoi_hydrogen_consumption(truck_data):
    """
    """
    # get german borders
    gdf = get_germany_gdf()

    # drop points outside germany
    truck_data_within = truck_data.loc[truck_data.within(gdf.geometry.iat[0])]

    poly_gdf = voronoi(truck_data_within, gdf)

    print("breaker")
