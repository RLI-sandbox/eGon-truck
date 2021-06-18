from src.io import read_egon_gpkgs, read_bast_data, export_results
from src.geo import check_membership
from src.demand import hydrogen_consumption

def run_egon_truck():
    egon_mv_grids = read_egon_gpkgs()

    bast_data = read_bast_data()

    bast_data["truck_data"] = check_membership(egon_mv_grids["mv_grid_district"], bast_data["truck_data"])

    egon_mv_grids["mv_grid_district"]["hydrogen_consumption"] = hydrogen_consumption(bast_data["truck_data"])

    egon_mv_grids["mv_grid_district"] = egon_mv_grids["mv_grid_district"].fillna(0)

    export_results(egon_mv_grids["mv_grid_district"])

if __name__ == "__main__":
    run_egon_truck()