import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.ops import cascaded_union
from geovoronoi import voronoi_regions_from_coords, points_to_coords


def mwe_geo():
    print("Please break here.")

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

def voronoi(points, boundary):
    """
    """
    # convert the boundary geometry into a union of the polygon
    # convert the Geopandas GeoSeries of Point objects to NumPy array of coordinates.
    boundary_shape = cascaded_union(boundary.geometry)
    coords = points_to_coords(points.geometry)

    # calculate Voronoi regions
    poly_shapes, pts, unassigned_pts = voronoi_regions_from_coords(coords, boundary_shape, return_unassigned_points=True)

    poly_gdf = gpd.GeoDataFrame(pd.DataFrame.from_dict(poly_shapes, orient="index", columns=["geometry"]))

    poly_gdf.index = [v[0] for v in pts.values()]

    return poly_gdf