import logging
import sys

from src.io import read_egon_gpkgs, read_bast_data, export_results, \
    get_federal_states_gdf
from src.geo import check_membership
from src.demand import blunt_hydrogen_consumption, voronoi_hydrogen_consumption


def run_egon_truck(
        mode="voronoi", target_mode="mv_grid_district"):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    logging.info("=" * 10 + f" Running {mode} mode " + "=" * 10)

    bast_data = read_bast_data()

    if target_mode == "mv_grid_district":
        egon_mv_grids = read_egon_gpkgs()
    elif target_mode == "federal_state":
        federal_states_gdf = get_federal_states_gdf()
    else:
        raise ValueError(f"Target {target_mode} does not exists.")

    if mode == "voronoi":
        if target_mode == "mv_grid_district":
            egon_mv_grids["mv_grid_district"] = voronoi_hydrogen_consumption(
                bast_data["truck_data"], egon_mv_grids["mv_grid_district"])
        elif target_mode == "federal_state":
            federal_states_gdf = voronoi_hydrogen_consumption(
                bast_data["truck_data"], federal_states_gdf)


    elif mode == "blunt":
        bast_data["truck_data"] = check_membership(
            egon_mv_grids["mv_grid_district"], bast_data["truck_data"])

        egon_mv_grids["mv_grid_district"]["hydrogen_consumption"] = \
            blunt_hydrogen_consumption(bast_data["truck_data"])

        egon_mv_grids["mv_grid_district"] = egon_mv_grids[
            "mv_grid_district"].fillna(0)

    else:
        raise ValueError(f"Mode {mode} is not supported.")

    if target_mode == "mv_grid_district":
        results = egon_mv_grids["mv_grid_district"]
    elif target_mode == "federal_state":
        results = federal_states_gdf

    export_results(
        results, mode=mode, target_mode=target_mode)

if __name__ == "__main__":
    run_egon_truck(target_mode="federal_state")
