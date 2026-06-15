import json
import os
import time

def load_dataset(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes           = data["nodes"]
    distance_matrix = data["distance_matrix"]

    node_names = [node["name"]      for node in nodes]
    weight_kg  = [node["weight_kg"] for node in nodes]
    hub_index  = next(i for i, node in enumerate(nodes) if node["type"] == "Hub")

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


def _nearest_neighbor(matriks: list, hub: int) -> tuple:
  
    n = len(matriks)
    dikunjungi = [False] * n
    rute = [hub]
    dikunjungi[hub] = True
    jarak = 0.0
    pos = hub

    for _ in range(n - 1):
        terdekat, d_min = -1, float("inf")
        for j in range(n):
            if not dikunjungi[j] and 0 < matriks[pos][j] < d_min:
                d_min, terdekat = matriks[pos][j], j
        if terdekat == -1:
            break
        rute.append(terdekat)
        dikunjungi[terdekat] = True
        jarak += d_min
        pos = terdekat

    jarak += matriks[pos][hub]
    rute.append(hub)
    return rute, jarak


class _State:
    __slots__ = ("rute_terbaik", "jarak_terbaik", "jumlah_node_dikunjungi", "jumlah_pruning")

    def __init__(self, rute_awal: list, jarak_awal: float):
        self.rute_terbaik            = rute_awal[:]
        self.jarak_terbaik           = jarak_awal
        self.jumlah_node_dikunjungi  = 0   # counter eksplorasi
        self.jumlah_pruning          = 0   # counter cabang yang dipangkas


def _dfs(
    pos         : int,
    dikunjungi  : list,
    rute_saat   : list,
    jarak_saat  : float,
    n           : int,
    matriks     : list,
    hub         : int,
    state       : _State,
) -> None:
    state.jumlah_node_dikunjungi += 1

    if len(rute_saat) == n:
        jarak_pulang = matriks[pos][hub]
        if jarak_pulang == 0 and pos != hub:
            return                         
        total = jarak_saat + jarak_pulang
        if total < state.jarak_terbaik:
            state.jarak_terbaik  = total
            state.rute_terbaik   = rute_saat[:] + [hub]
        return

    for tetangga in range(n):
        if dikunjungi[tetangga]:
            continue

        jarak_langkah = matriks[pos][tetangga]

        if jarak_langkah == 0:
            continue

        jarak_baru = jarak_saat + jarak_langkah

        if jarak_baru >= state.jarak_terbaik:
            state.jumlah_pruning += 1
            continue

        dikunjungi[tetangga] = True
        rute_saat.append(tetangga)

        _dfs(
            pos        = tetangga,
            dikunjungi = dikunjungi,
            rute_saat  = rute_saat,
            jarak_saat = jarak_baru,
            n          = n,
            matriks    = matriks,
            hub        = hub,
            state      = state,
        )

        rute_saat.pop()
        dikunjungi[tetangga] = False


def dfs_backtracking_tsp(matriks: list, hub: int = 0) -> tuple:
    n = len(matriks)

    rute_nn, jarak_nn = _nearest_neighbor(matriks, hub)

    state      = _State(rute_nn, jarak_nn)
    dikunjungi = [False] * n
    dikunjungi[hub] = True

    waktu_mulai = time.perf_counter()

    _dfs(
        pos        = hub,
        dikunjungi = dikunjungi,
        rute_saat  = [hub],
        jarak_saat = 0.0,
        n          = n,
        matriks    = matriks,
        hub        = hub,
        state      = state,
    )

    waktu_selesai = time.perf_counter()

    stats = {
        "node_dieksplorasi" : state.jumlah_node_dikunjungi,
        "cabang_dipangkas"  : state.jumlah_pruning,
        "waktu_detik"       : round(waktu_selesai - waktu_mulai, 6),
        "upper_bound_awal"  : jarak_nn,   # dari Nearest Neighbor
        "rute_nn"           : rute_nn,
    }

    return state.rute_terbaik, state.jarak_terbaik, stats


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
        asal        = rute[i]
        tujuan      = rute[i + 1]
        jarak       = matriks[asal][tujuan]
        rasio       = cfg.rasio_kosong + (beban_sekarang / cfg.beban_maks) * (
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
    stats       : dict,
) -> None:
    lebar = 84
    SEP   = "=" * lebar
    sep   = "-" * (lebar - 2)

    print(SEP)
    print("   LAPORAN OPTIMASI RUTE TSP – DFS BACKTRACKING + PRUNING")
    print("   Metode: Exhaustive Search dengan Bound Pruning (Solusi Optimal 100%)")
    print(SEP)


    print()
    print("  [ STATISTIK PENCARIAN ]")
    print(f"  Upper-bound awal (Nearest Neighbor) : {stats['upper_bound_awal']:.2f} km")
    print(f"  Node dieksplorasi                   : {stats['node_dieksplorasi']:,}")
    print(f"  Cabang dipangkas (pruning)          : {stats['cabang_dipangkas']:,}")
    print(f"  Waktu komputasi                     : {stats['waktu_detik']:.6f} detik")


    selisih = stats["upper_bound_awal"] - total_jarak
    persen  = (selisih / stats["upper_bound_awal"] * 100) if stats["upper_bound_awal"] > 0 else 0
    print(f"  Perbaikan vs Nearest Neighbor       : {selisih:.2f} km ({persen:.2f}%)")

  
    print()
    print("  [ RUTE OPTIMAL ]")
    rute_str = " → ".join(node_names[n] for n in rute)
    print(f"  {rute_str}")
    print()
    print(f"  Total Jarak : {total_jarak:.2f} km")
    print(f"  Total BBM   : {total_liter:.4f} liter")

    print()
    print("  [ DETAIL SEGMEN PERJALANAN ]")
    print(f"  {'No':>3}  {'Dari':<14} {'Ke':<14} {'Jarak':>7} {'Beban':>9} {'Rasio':>10} {'Liter':>8}")
    print("  " + sep)

    for i, seg in enumerate(detail, 1):
        print(
            f"  {i:>3}  {node_names[seg['dari']]:<14} {node_names[seg['ke']]:<14}"
            f"  {seg['jarak_km']:>5} km"
            f"  {seg['beban_kg']:>7.3f} kg"
            f"  {seg['rasio_L_km']:>9.6f}"
            f"  {seg['liter']:>6.4f} L"
        )

    print("  " + sep)
    print(
        f"  {'TOT':>3}  {'':14} {'':14}"
        f"  {total_jarak:>5.0f} km"
        f"  {'':>9}"
        f"  {'':>10}"
        f"  {total_liter:>6.4f} L"
    )
    print(SEP)


if __name__ == "__main__":


    base_dir  = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "..", "..", "data", "dataset.json")

    print(f"  Memuat dataset dari : {os.path.normpath(json_path)}")

    dataset         = load_dataset(json_path)
    node_names      = dataset["node_names"]
    weight_kg       = dataset["weight_kg"]
    distance_matrix = dataset["distance_matrix"]
    hub_index       = dataset["hub_index"]

    total_muatan = sum(w for i, w in enumerate(weight_kg) if i != hub_index)

    print(f"  Hub                 : {node_names[hub_index]}")
    print(f"  Jumlah node         : {len(node_names)} ({len(node_names)-1} pelanggan + 1 hub)")
    print(f"  Muatan awal         : {total_muatan:.2f} kg")
    print()

    cfg = KonfigurasiKendaraan(
        beban_awal     = total_muatan,
        beban_per_stop = weight_kg,
        beban_maks     = total_muatan,
        rasio_penuh    = 0.05,
        rasio_kosong   = 0.02,
    )

    print("  Menjalankan DFS Backtracking + Pruning...")
    print("  (Mengeksplorasi semua permutasi rute yang mungkin)\n")


    rute, total_jarak, stats = dfs_backtracking_tsp(distance_matrix, hub=hub_index)

    total_liter, detail = hitung_bensin(rute, distance_matrix, cfg, hub=hub_index)

    cetak_laporan(rute, total_jarak, total_liter, detail, node_names, stats)