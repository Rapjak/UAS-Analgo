import os
import time
import matplotlib.pyplot as plt
import argparse

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
docs_dir = os.path.join(base_dir, "..", "docs")
os.makedirs(docs_dir, exist_ok=True)

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

parser = argparse.ArgumentParser()

parser.add_argument(
    "--scenario",
    choices=["subsidy", "crisis", "all"],
    default="all"
)

args = parser.parse_args()

def simpan_grafik(
    nama_file,
    judul,
    labels,
    values,
    ylabel,
):
    plt.figure(figsize=(8, 5))

    plt.bar(labels, values)

    plt.title(judul)
    plt.ylabel(ylabel)

    plt.tight_layout()

    output_path = os.path.join(
        docs_dir,
        nama_file
    )

    plt.savefig(output_path)

    plt.close()

    print(f"Grafik disimpan: {output_path}")

def simpan_grafik_break_even():
    harga_range = range(0, 6000000, 50000)

    tco_greedy = [
        (liter_greedy * h)
        + (waktu_greedy_ms * BIAYA_KOMPUTASI_PER_MS)
        for h in harga_range
    ]

    tco_dfs = [
        (liter_dfs * h)
        + (waktu_dfs_ms * BIAYA_KOMPUTASI_PER_MS)
        for h in harga_range
    ]

    plt.figure(figsize=(10, 6))

    plt.plot(
        harga_range,
        tco_greedy,
        label="Greedy"
    )

    plt.plot(
        harga_range,
        tco_dfs,
        label="DFS + Pruning"
    )

    plt.xlabel("Harga BBM (Rp/L)")
    plt.ylabel("TCO (Rp)")
    plt.title("Break-Even Analysis")

    plt.grid(True)
    plt.legend()

    output_path = os.path.join(
        docs_dir,
        "grafik_break_even.png"
    )

    plt.savefig(output_path)
    plt.close()

    print(f"Grafik disimpan: {output_path}")

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

if args.scenario in ["subsidy", "all"]:
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

if args.scenario in ["crisis", "all"]:
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

penghematan_jarak = jarak_greedy - jarak_dfs

persen_jarak = (
    penghematan_jarak / jarak_greedy
) * 100

penghematan_bbm = liter_greedy - liter_dfs

persen_bbm = (
    penghematan_bbm / liter_greedy
) * 100

biaya_komputasi_greedy = (
    waktu_greedy_ms * BIAYA_KOMPUTASI_PER_MS
)

biaya_komputasi_dfs = (
    waktu_dfs_ms * BIAYA_KOMPUTASI_PER_MS
)

selisih_bbm = liter_greedy - liter_dfs

if abs(selisih_bbm) > 1e-9:
    break_even = (
        biaya_komputasi_dfs
        - biaya_komputasi_greedy
    ) / selisih_bbm
else:
    break_even = float("inf")

print("\n")
print("=" * 85)
print("KESIMPULAN")
print("=" * 85)

# Grafik perbandingan jarak
simpan_grafik(
    "grafik_jarak.png",
    "Perbandingan Total Jarak",
    ["Greedy", "DFS"],
    [jarak_greedy, jarak_dfs],
    "Kilometer"
)

#Grafik TCO subsidi
simpan_grafik(
    "grafik_tco_subsidi.png",
    "Perbandingan TCO - Skenario Subsidi",
    ["Greedy", "DFS"],
    [tco_greedy_subsidi, tco_dfs_subsidi],
    "Rupiah"
)

# Grafik TCO krisis
simpan_grafik(
    "grafik_tco_krisis.png",
    "Perbandingan TCO - Skenario Krisis",
    ["Greedy", "DFS"],
    [tco_greedy_krisis, tco_dfs_krisis],
    "Rupiah"
)

# Grafik break-even point
simpan_grafik_break_even()

print("=" * 85)

print(
    f"DFS menghasilkan rute {penghematan_jarak:.2f} km "
    f"lebih pendek ({persen_jarak:.2f}%)."
)

print(
    f"DFS menghemat {penghematan_bbm:.4f} liter "
    f"BBM ({persen_bbm:.2f}%)."
)

print(
    f"Break-even terjadi pada harga BBM sekitar "
    f"Rp{break_even:,.0f}/liter."
)

if tco_greedy_subsidi < tco_dfs_subsidi:
    print(
        "Pada skenario subsidi, Greedy memiliki "
        "TCO lebih rendah."
    )

if tco_greedy_krisis < tco_dfs_krisis:
    print(
        "Pada skenario krisis, Greedy tetap memiliki "
        "TCO lebih rendah."
    )

print(
    "Rekomendasi: gunakan Greedy untuk operasional "
    "harian dan DFS untuk validasi atau analisis "
    "rute optimal."
)