import numpy as np


def check_membership(grid_districts, truck_data):
    """ Maps BAST counting stations to the MV grid districts
    """
    truck_data = truck_data.assign(mv_grid_district=np.nan)

    # within
    for idx, polygon in grid_districts.geometry.items():
        mask = truck_data.within(polygon)

        if mask.any():
            if truck_data[mask].mv_grid_district.sum() > 0:
                raise ValueError("Checkpoint is within two or more grid districts.\n", truck_data[mask].dropna(),
                                 "\nAre also in MV grid district {}.".format(idx))

            truck_data[mask] = truck_data[mask].assign(mv_grid_district=idx)

    # if any point is not within any polygon use the closest
    if len(truck_data.loc[truck_data.mv_grid_district.isna()]) > 0:
        for idx, point in truck_data.loc[truck_data.mv_grid_district.isna()].geometry.items():
            polygon_index = grid_districts.distance(point).sort_values().index[0]

            truck_data.at[idx, "mv_grid_district"] = polygon_index

    truck_data.mv_grid_district = truck_data.mv_grid_district.astype(np.uint16)

    return truck_data