import logging
import sys

from egon_truck.data_io import (
    export_results,
    read_bast_data,
    read_egon_gpkgs,
    read_nuts_3,
)
from egon_truck.demand import blunt_hydrogen_consumption, voronoi_hydrogen_consumption
from egon_truck.geo import check_membership

MODE: str = "voronoi"
SCENARIO: str = "nep_scenario"
TARGET: str = "nuts-3"


def run_egon_truck(
    mode: str = "voronoi",
    scenario: str = "nep_scenario",
    target: str = "mvgd",
):
    """
    Possible options for mode are "voronoi" or "blunt". For scenario they are
    "nep_scenario" or "egon_scenario". You can add your own scenarios within the
    config/settings.toml.
    """
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    logging.info("=" * 10 + f" Running {mode} mode " + "=" * 10)

    if target == "mvgd":
        egon_mv_grids = read_egon_gpkgs()
        target_gdf = egon_mv_grids["mv_grid_district"]
    elif target == "nuts-3":
        target_gdf = read_nuts_3()
    else:
        raise ValueError(f"Target {target} does not exist.")

    bast_data = read_bast_data()

    if mode == "voronoi":
        target_gdf = voronoi_hydrogen_consumption(
            bast_data["truck_data"],
            target_gdf,
            scenario=scenario,
        )

    elif mode == "blunt":
        bast_data["truck_data"] = check_membership(target_gdf, bast_data["truck_data"])

        target_gdf["hydrogen_consumption"] = blunt_hydrogen_consumption(
            bast_data["truck_data"],
            scenario=scenario,
        )

        target_gdf = target_gdf.fillna(0)

    else:
        raise ValueError(f"Mode {mode} is not supported.")

    export_results(
        target_gdf,
        mode=mode,
        scenario=scenario,
        target=target,
    )


if __name__ == "__main__":
    run_egon_truck(
        mode=MODE,
        scenario=SCENARIO,
        target=TARGET,
    )
