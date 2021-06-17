from config.config import settings


def hydrogen_consumption(truck_data):
    """
    """
    hgv_amount = settings.hgv_amount
    hgv_mean_mileage = settings.hgv_mean_mileage # km/a
    hydrogen_consumption = settings.hydrogen_consumption # kg/100km
    relevant_columns = settings.relevant_columns

    hydrogen_consumption_per_km = hydrogen_consumption / 100 # kg/km

    # calculate total hydrogen consumption
    total_hydrogen_demand = hgv_amount * hgv_mean_mileage * hydrogen_consumption_per_km # kg/a

    # distribute consumption
    traffic_volume = truck_data.groupby(by="mv_grid_district").agg({relevant_columns[0]: sum})
    print("break")
