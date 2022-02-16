import logging

import geopandas as gpd
import numpy as np
import pandas as pd

from geovoronoi import points_to_coords, voronoi_regions_from_coords
from shapely.ops import cascaded_union

from config.config import settings

log = logging.getLogger(__name__)


def check_membership(grid_districts, truck_data):
    """Maps BAST counting stations to the MV grid districts"""
    log.info("Mapping BAST counting stations to MV Grid Districts.")

    truck_data = truck_data.assign(mv_grid_district=np.nan)

    # within
    for idx, polygon in grid_districts.geometry.items():
        mask = truck_data.within(polygon)

        if mask.any():
            if truck_data[mask].mv_grid_district.sum() > 0:
                raise ValueError(
                    "Checkpoint is within two or more grid districts.\n",
                    truck_data[mask].dropna(),
                    "\nAre also in MV grid district {}.".format(idx),
                )

            truck_data[mask] = truck_data[mask].assign(mv_grid_district=idx)

    # if any point is not within any polygon use the closest
    if len(truck_data.loc[truck_data.mv_grid_district.isna()]) > 0:
        for idx, point in truck_data.loc[
            truck_data.mv_grid_district.isna()
        ].geometry.items():
            polygon_index = grid_districts.distance(point).sort_values().index[0]

            truck_data.at[idx, "mv_grid_district"] = polygon_index

    truck_data.mv_grid_district = truck_data.mv_grid_district.astype(np.uint16)

    log.info("Done.")

    return truck_data


def voronoi(points, boundary):
    """Building a Voronoi Field from points and a boundary"""
    truck_col = settings.relevant_columns[0]
    log.info("Building Voronoi Field.")

    epsg = settings.egon_epsg

    # convert the boundary geometry into a union of the polygon
    # convert the Geopandas GeoSeries of Point objects to NumPy array of coordinates.
    boundary_shape = cascaded_union(boundary.geometry)
    coords = points_to_coords(points.geometry)

    # calculate Voronoi regions
    poly_shapes, pts, unassigned_pts = voronoi_regions_from_coords(
        coords, boundary_shape, return_unassigned_points=True
    )

    poly_gdf = gpd.GeoDataFrame(
        pd.DataFrame.from_dict(poly_shapes, orient="index", columns=["geometry"])
    )

    # match points to old index
    # FIXME: This seems overcomplicated
    poly_gdf.index = [v[0] for v in pts.values()]

    poly_gdf = poly_gdf.sort_index()

    unmatched = [points.index[idx] for idx in unassigned_pts]

    points_matched = points.drop(unmatched)

    poly_gdf.index = points_matched.index

    # match truck traffic to new polys
    poly_gdf = poly_gdf.assign(truck_traffic=points.loc[poly_gdf.index][truck_col])

    poly_gdf = poly_gdf.set_crs(epsg=epsg, inplace=True)

    log.info("Done.")

    return poly_gdf


def geo_intersect(voronoi_gdf, grid_districts, mode="intersection"):
    """Calculate Intersections between two GeoDataFrames and distribute truck traffic"""
    log.info(
        "Calculating Intersections between Voronoi Field and Grid Districts\n"
        + "and distributing truck traffic accordingly to the area share."
    )
    voronoi_gdf = voronoi_gdf.assign(voronoi_id=voronoi_gdf.index.tolist())

    # Find Intersections between both GeoDataFrames
    intersection_gdf = gpd.overlay(
        voronoi_gdf, grid_districts[["subst_id", "geometry"]], how=mode
    )

    # Calc Area of Intersections
    intersection_gdf = intersection_gdf.assign(
        surface_area=intersection_gdf.geometry.area / 10**6
    )  # km²

    # Initialize results column
    grid_districts = grid_districts.assign(truck_traffic=0)

    grid_districts.index = grid_districts.subst_id.tolist()

    for voronoi_id in intersection_gdf.voronoi_id.unique():
        voronoi_id_intersection_gdf = intersection_gdf.loc[
            intersection_gdf.voronoi_id == voronoi_id
        ]

        total_area = voronoi_id_intersection_gdf.surface_area.sum()

        truck_traffic = voronoi_id_intersection_gdf.truck_traffic.iat[0]

        for idx, row in voronoi_id_intersection_gdf.iterrows():
            traffic_share = truck_traffic * row["surface_area"] / total_area

            grid_districts.at[row["subst_id"], "truck_traffic"] += traffic_share

    log.info("Done.")

    return grid_districts
