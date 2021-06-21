import logging

from src.io import read_egon_gpkgs, read_bast_data, export_results
from src.geo import check_membership
from src.demand import blunt_hydrogen_consumption, voronoi_hydrogen_consumption

def run_egon_truck(mode="voronoi"):
    logging.basicConfig(filename='egon_truck.log', level=logging.INFO)

    logging.info("="*10 + f" Running {mode} mode " + "="*10)

    egon_mv_grids = read_egon_gpkgs()

    bast_data = read_bast_data()

    if mode == "voronoi":
        egon_mv_grids["mv_grid_district"] = voronoi_hydrogen_consumption(
            bast_data["truck_data"], egon_mv_grids["mv_grid_district"])

    elif mode == "blunt":
        bast_data["truck_data"] = check_membership(egon_mv_grids["mv_grid_district"], bast_data["truck_data"])

        egon_mv_grids["mv_grid_district"]["hydrogen_consumption"] = blunt_hydrogen_consumption(
            bast_data["truck_data"])

        egon_mv_grids["mv_grid_district"] = egon_mv_grids["mv_grid_district"].fillna(0)
    else:
        raise ValueError(f"Mode {mode} is not supported.")

    export_results(egon_mv_grids["mv_grid_district"], mode=mode)

if __name__ == "__main__":
    run_egon_truck()