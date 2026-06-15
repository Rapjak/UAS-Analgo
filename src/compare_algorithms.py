import os
import time

from algorithms.tsp_greedy import (
    load_dataset,
    greedy_tsp,
    KonfigurasiKendaraan,
    hitung_bensin
)

from algorithms.exact_algorithm import (
    dfs_backtracking_tsp
)

base_dir = os.path.dirname(os.path.abspath(__file__))

json_path = os.path.join(
    base_dir,
    "..",
    "data",
    "dataset.json"
)

dataset = load_dataset(json_path)
total_muatan = sum(
    w
    for i, w in enumerate(dataset["weight_kg"])
    if i != dataset["hub_index"]
)

cfg = KonfigurasiKendaraan(
    beban_awal=total_muatan,
    beban_per_stop=dataset["weight_kg"],
    beban_maks=total_muatan,
    rasio_penuh=0.05,
    rasio_kosong=0.02
)

HARGA_BBM_SUBSIDI = 5000
HARGA_BBM_KRISIS  = 20000

BIAYA_KOMPUTASI_PER_MS = 50

print("Jumlah node :", len(dataset["node_names"]))

start = time.perf_counter()

rute_greedy, jarak_greedy = greedy_tsp(
    dataset["distance_matrix"],
    dataset["hub_index"]
)

end = time.perf_counter()

waktu_greedy_ms = (end - start) * 1000

liter_greedy, detail_greedy = hitung_bensin(
    rute_greedy,
    dataset["distance_matrix"],
    cfg,
    dataset["hub_index"]
)

tco_greedy_subsidi = (
    liter_greedy * HARGA_BBM_SUBSIDI
) + (
    waktu_greedy_ms * BIAYA_KOMPUTASI_PER_MS
)

tco_greedy_krisis = (
    liter_greedy * HARGA_BBM_KRISIS
) + (
    waktu_greedy_ms * BIAYA_KOMPUTASI_PER_MS
)

print("\nHASIL GREEDY")
print("Rute :", rute_greedy)
print("Jarak:", jarak_greedy)

start = time.perf_counter()

rute_dfs, jarak_dfs, stats_dfs = dfs_backtracking_tsp(
    dataset["distance_matrix"],
    dataset["hub_index"]
)

end = time.perf_counter()

waktu_dfs_ms = (end - start) * 1000

liter_dfs, detail_dfs = hitung_bensin(
    rute_dfs,
    dataset["distance_matrix"],
    cfg,
    dataset["hub_index"]
)

tco_dfs_subsidi = (
    liter_dfs * HARGA_BBM_SUBSIDI
) + (
    waktu_dfs_ms * BIAYA_KOMPUTASI_PER_MS
)

tco_dfs_krisis = (
    liter_dfs * HARGA_BBM_KRISIS
) + (
    waktu_dfs_ms * BIAYA_KOMPUTASI_PER_MS
)

print("\nHASIL DFS")
print("Rute :", rute_dfs)
print("Jarak:", jarak_dfs)

print("\nStatistik:")
print("Node dieksplorasi :", stats_dfs["node_dieksplorasi"])
print("Cabang dipangkas  :", stats_dfs["cabang_dipangkas"])
print("Waktu             :", stats_dfs["waktu_detik"], "detik")

print("\n")
print("=" * 70)
print("PERBANDINGAN ALGORITMA")
print("=" * 70)

print(
    f"{'METODE':<20}"
    f"{'JARAK(km)':>12}"
    f"{'BBM(L)':>12}"
    f"{'WAKTU(ms)':>15}"
)

print("-" * 70)

print(
    f"{'GREEDY':<20}"
    f"{jarak_greedy:>12.2f}"
    f"{liter_greedy:>12.4f}"
    f"{waktu_greedy_ms:>15.4f}"
)

print(
    f"{'DFS+PRUNING':<20}"
    f"{jarak_dfs:>12.2f}"
    f"{liter_dfs:>12.4f}"
    f"{waktu_dfs_ms:>15.4f}"
)

print("=" * 70)

print("\n")
print("=" * 85)
print("SKENARIO SUBSIDI (Rp5.000/L)")
print("=" * 85)

print(
    f"{'METODE':<20}"
    f"{'JARAK':>10}"
    f"{'BBM':>12}"
    f"{'WAKTU':>12}"
    f"{'TCO':>18}"
)

print("-" * 85)

print(
    f"{'GREEDY':<20}"
    f"{jarak_greedy:>10.2f}"
    f"{liter_greedy:>12.4f}"
    f"{waktu_greedy_ms:>12.4f}"
    f"{tco_greedy_subsidi:>18,.2f}"
)

print(
    f"{'DFS+PRUNING':<20}"
    f"{jarak_dfs:>10.2f}"
    f"{liter_dfs:>12.4f}"
    f"{waktu_dfs_ms:>12.4f}"
    f"{tco_dfs_subsidi:>18,.2f}"
)

print("\n")
print("=" * 85)
print("SKENARIO KRISIS (Rp20.000/L)")
print("=" * 85)

print(
    f"{'METODE':<20}"
    f"{'JARAK':>10}"
    f"{'BBM':>12}"
    f"{'WAKTU':>12}"
    f"{'TCO':>18}"
)

print("-" * 85)

print(
    f"{'GREEDY':<20}"
    f"{jarak_greedy:>10.2f}"
    f"{liter_greedy:>12.4f}"
    f"{waktu_greedy_ms:>12.4f}"
    f"{tco_greedy_krisis:>18,.2f}"
)

print(
    f"{'DFS+PRUNING':<20}"
    f"{jarak_dfs:>10.2f}"
    f"{liter_dfs:>12.4f}"
    f"{waktu_dfs_ms:>12.4f}"
    f"{tco_dfs_krisis:>18,.2f}"
)

print("\n")
print("=" * 85)
print("KESIMPULAN")
print("=" * 85)

if tco_greedy_subsidi < tco_dfs_subsidi:
    print("Pada skenario subsidi, Greedy lebih ekonomis.")
else:
    print("Pada skenario subsidi, DFS lebih ekonomis.")

if tco_greedy_krisis < tco_dfs_krisis:
    print("Pada skenario krisis, Greedy lebih ekonomis.")
else:
    print("Pada skenario krisis, DFS lebih ekonomis.")