from src.io import read_egon_gpkgs, read_bast_data

def run_egon_truck():
    egon_mv_grids = read_egon_gpkgs()

    bast_data = read_bast_data()

    print(egon_mv_grids)

if __name__ == "__main__":
    run_egon_truck()