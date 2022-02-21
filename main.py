import logging
import sys

from egon_truck.data_io import export_results, read_bast_data, read_egon_gpkgs
from egon_truck.demand import blunt_hydrogen_consumption, voronoi_hydrogen_consumption
from egon_truck.geo import check_membership

MODE: str = "voronoi"
SCENARIO: str = "nep_scenario"


def run_egon_truck(
    mode: str = "voronoi",
    scenario: str = "nep_scenario",
):
    """
    Possible options for mode are "voronoi" or "blunt". For scenario they are
    "nep_scenario" or "egon_scenario". You can add your own scenarios within the
    config/settings.toml.
    """
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    logging.info("=" * 10 + f" Running {mode} mode " + "=" * 10)

    egon_mv_grids = read_egon_gpkgs()

    bast_data = read_bast_data()

    if mode == "voronoi":
        egon_mv_grids["mv_grid_district"] = voronoi_hydrogen_consumption(
            bast_data["truck_data"],
            egon_mv_grids["mv_grid_district"],
            scenario=scenario,
        )

    elif mode == "blunt":
        bast_data["truck_data"] = check_membership(
            egon_mv_grids["mv_grid_district"], bast_data["truck_data"]
        )

        egon_mv_grids["mv_grid_district"][
            "hydrogen_consumption"
        ] = blunt_hydrogen_consumption(
            bast_data["truck_data"],
            scenario=scenario,
        )

        egon_mv_grids["mv_grid_district"] = egon_mv_grids["mv_grid_district"].fillna(0)

    else:
        raise ValueError(f"Mode {mode} is not supported.")

    export_results(
        egon_mv_grids["mv_grid_district"],
        mode=mode,
        scenario=scenario,
    )


if __name__ == "__main__":
    run_egon_truck(
        mode=MODE,
        scenario=SCENARIO,
    )
