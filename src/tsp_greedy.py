

import json
import os


def load_dataset(json_path: str) -> dict:
  
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes           = data["nodes"]
    distance_matrix = data["distance_matrix"]

    node_names = [node["name"] for node in nodes]
    weight_kg  = [node["weight_kg"] for node in nodes]


    hub_index = next(i for i, node in enumerate(nodes) if node["type"] == "Hub")

    return {
        "node_names"      : node_names,
        "weight_kg"       : weight_kg,
        "distance_matrix" : distance_matrix,
        "hub_index"       : hub_index,
    }


class KonfigurasiKendaraan:
   
    def __init__(
        self,
        beban_awal    : float,
        beban_per_stop: list,
        beban_maks    : float,
        rasio_penuh   : float = 0.05,
        rasio_kosong  : float = 0.02,
    ):
        self.beban_awal     = beban_awal
        self.beban_per_stop = beban_per_stop
        self.beban_maks     = beban_maks
        self.rasio_penuh    = rasio_penuh
        self.rasio_kosong   = rasio_kosong


def greedy_tsp(matriks: list, hub: int = 0) -> tuple:
   
    n = len(matriks)
    dikunjungi = [False] * n
    rute = [hub]
    dikunjungi[hub] = True
    total_jarak = 0.0
    posisi_sekarang = hub

    for _ in range(n - 1):
        jarak_terdekat = float("inf")
        node_terdekat  = -1

        for j in range(n):
            if not dikunjungi[j] and matriks[posisi_sekarang][j] < jarak_terdekat:
                jarak_terdekat = matriks[posisi_sekarang][j]
                node_terdekat  = j

        if node_terdekat == -1:
            break

        rute.append(node_terdekat)
        dikunjungi[node_terdekat] = True
        total_jarak += jarak_terdekat
        posisi_sekarang = node_terdekat

    # Kembali ke Hub
    total_jarak += matriks[posisi_sekarang][hub]
    rute.append(hub)

    return rute, total_jarak


def hitung_bensin(
    rute   : list,
    matriks: list,
    cfg    : KonfigurasiKendaraan,
    hub    : int = 0,
) -> tuple:
    
    beban_map      = {i: w for i, w in enumerate(cfg.beban_per_stop)}
    beban_sekarang = cfg.beban_awal
    total_liter    = 0.0
    detail_segmen  = []

    for i in range(len(rute) - 1):
        asal   = rute[i]
        tujuan = rute[i + 1]
        jarak  = matriks[asal][tujuan]

        rasio        = cfg.rasio_kosong + (beban_sekarang / cfg.beban_maks) * (
                           cfg.rasio_penuh - cfg.rasio_kosong)
        liter_segmen = jarak * rasio

        detail_segmen.append({
            "dari"      : asal,
            "ke"        : tujuan,
            "jarak_km"  : jarak,
            "beban_kg"  : round(beban_sekarang, 3),
            "rasio_L_km": round(rasio, 6),
            "liter"     : round(liter_segmen, 4),
        })

        total_liter += liter_segmen

        if tujuan != hub:
            beban_sekarang = max(0.0, beban_sekarang - beban_map.get(tujuan, 0.0))

    return round(total_liter, 4), detail_segmen


def cetak_laporan(
    rute        : list,
    total_jarak : float,
    total_liter : float,
    detail      : list,
    node_names  : list,
) -> None:
    lebar = 82
    print("=" * lebar)
    print("   LAPORAN OPTIMASI RUTE TSP – GREEDY NEAREST NEIGHBOR")
    print("=" * lebar)

    rute_str = " → ".join(node_names[n] for n in rute)
    print(f"\n  Rute       : {rute_str}")
    print(f"  Total Jarak: {total_jarak:.2f} km")
    print(f"  Total BBM  : {total_liter:.4f} liter\n")

    print(f"  {'No':>3}  {'Dari':<14} {'Ke':<14} {'Jarak':>7} {'Beban':>9} {'Rasio':>10} {'Liter':>8}")
    print("  " + "-" * (lebar - 2))

    for i, seg in enumerate(detail, 1):
        print(
            f"  {i:>3}  {node_names[seg['dari']]:<14} {node_names[seg['ke']]:<14}"
            f"  {seg['jarak_km']:>5} km"
            f"  {seg['beban_kg']:>7.3f} kg"
            f"  {seg['rasio_L_km']:>9.6f}"
            f"  {seg['liter']:>6.4f} L"
        )

    print("  " + "-" * (lebar - 2))
    print(f"  {'TOT':>3}  {'':14} {'':14}  {total_jarak:>5.0f} km  {'':>7}   {'':>9}  {total_liter:>6.4f} L")
    print("=" * lebar)


if __name__ == "__main__":

  
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "..", "data", "dataset.json")

    print(f"  Memuat dataset dari: {os.path.normpath(json_path)}\n")
    dataset = load_dataset(json_path)

    node_names      = dataset["node_names"]
    weight_kg       = dataset["weight_kg"]
    distance_matrix = dataset["distance_matrix"]
    hub_index       = dataset["hub_index"]

  
    total_muatan = sum(w for i, w in enumerate(weight_kg) if i != hub_index)

    print(f"  Hub          : {node_names[hub_index]}")
    print(f"  Muatan awal  : {total_muatan:.2f} kg")
    print(f"  Bobot paket  : { {node_names[i]: weight_kg[i] for i in range(len(node_names)) if i != hub_index} }\n")

    cfg = KonfigurasiKendaraan(
        beban_awal     = total_muatan,
        beban_per_stop = weight_kg,      
        beban_maks     = total_muatan,   
        rasio_penuh    = 0.05,           
        rasio_kosong   = 0.02,           
    )

    rute, total_jarak  = greedy_tsp(distance_matrix, hub=hub_index)
    total_liter, detail = hitung_bensin(rute, distance_matrix, cfg, hub=hub_index)

    cetak_laporan(rute, total_jarak, total_liter, detail, node_names)