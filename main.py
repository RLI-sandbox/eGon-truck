import logging
import sys

from egon_truck.demand import blunt_hydrogen_consumption, voronoi_hydrogen_consumption
from egon_truck.geo import check_membership
from egon_truck.io import export_results, read_bast_data, read_egon_gpkgs


def run_egon_truck(mode="voronoi"):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    logging.info("=" * 10 + f" Running {mode} mode " + "=" * 10)

    egon_mv_grids = read_egon_gpkgs()

    bast_data = read_bast_data()

    if mode == "voronoi":
        egon_mv_grids["mv_grid_district"] = voronoi_hydrogen_consumption(
            bast_data["truck_data"], egon_mv_grids["mv_grid_district"]
        )

    elif mode == "blunt":
        bast_data["truck_data"] = check_membership(
            egon_mv_grids["mv_grid_district"], bast_data["truck_data"]
        )

        egon_mv_grids["mv_grid_district"][
            "hydrogen_consumption"
        ] = blunt_hydrogen_consumption(bast_data["truck_data"])

        egon_mv_grids["mv_grid_district"] = egon_mv_grids["mv_grid_district"].fillna(0)

    else:
        raise ValueError(f"Mode {mode} is not supported.")

    export_results(egon_mv_grids["mv_grid_district"], mode=mode)


if __name__ == "__main__":
    run_egon_truck()
