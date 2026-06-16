# UAS Analisis Algoritma

## Optimasi Rute Last-Mile Delivery Menggunakan Greedy dan DFS Backtracking + Pruning

---

# 1. Cara Menjalankan Program

Pastikan berada pada root project:

```bash
python src/compare_algorithms.py
```

Program akan:

* Membaca dataset dari file JSON eksternal
* Menjalankan algoritma Greedy
* Menjalankan algoritma DFS Backtracking + Pruning
* Menghitung konsumsi BBM
* Menghitung waktu eksekusi
* Menghitung Total Cost of Ownership (TCO)
* Menampilkan komparasi hasil pada terminal

---

# 2. Pemilihan Algoritma

## Algoritma A: Greedy Nearest Neighbor

Algoritma Greedy bekerja dengan memilih lokasi pelanggan terdekat yang belum dikunjungi pada setiap langkah.

Kelebihan:

* Eksekusi sangat cepat
* Konsumsi resource server sangat kecil
* Cocok untuk jumlah pelanggan besar

Kekurangan:

* Tidak menjamin solusi optimal
* Dapat menghasilkan jarak tempuh lebih panjang

Hasil eksperimen:

* Total Jarak: 66 km
* Konsumsi BBM: 2.1145 liter
* Waktu Eksekusi: 0.0559 ms

---

## Algoritma B: DFS Backtracking + Pruning

Algoritma DFS melakukan eksplorasi seluruh kemungkinan rute yang valid.

Pruning digunakan untuk memangkas cabang yang sudah pasti lebih buruk dibanding solusi terbaik saat ini.

Kelebihan:

* Menjamin solusi optimal
* Menghasilkan jarak minimum global

Kekurangan:

* Waktu komputasi sangat tinggi
* Kurang cocok untuk jumlah node besar

Hasil eksperimen:

* Total Jarak: 57 km
* Konsumsi BBM: 2.0790 liter
* Waktu Eksekusi: 3540.4715 ms

---

# 3. Analisis Kompleksitas

## Greedy Nearest Neighbor

### Time Complexity

Pada setiap langkah algoritma mencari node terdekat dari seluruh node yang belum dikunjungi.

Terdapat:

* n langkah perjalanan
* setiap langkah memeriksa hingga n node

Sehingga:

O(n²)

### Space Complexity

Menyimpan:

* daftar node yang sudah dikunjungi
* rute hasil

Sehingga:

O(n)

---

## DFS Backtracking + Pruning

### Time Complexity

DFS mengeksplorasi seluruh kemungkinan permutasi rute.

Jumlah kemungkinan rute:

(n - 1)!

Karena setiap pelanggan dapat muncul pada urutan berbeda.

Sehingga:

O(n!)

Pruning mampu mengurangi eksplorasi aktual tetapi tidak mengubah kompleksitas terburuk.

### Space Complexity

Menyimpan:

* stack rekursi
* daftar node yang dikunjungi
* rute sementara

Sehingga:

O(n)

---

# 4. Hasil Eksperimen

| Metrik | Greedy    | DFS + Pruning |
| ------ | --------- | ------------- |
| Jarak  | 66 km     | 57 km         |
| BBM    | 2.1145 L  | 2.0790 L      |
| Waktu  | 0.0559 ms | 3540.4715 ms  |

Perbaikan jarak DFS:

57 km vs 66 km

Penghematan:

9 km (13.64%)

---

# 5. Analisis TCO

## Skenario Subsidi

Harga BBM:

Rp5.000/L

| Algoritma |       TCO |
| --------- | --------: |
| Greedy    |  Rp10.575 |
| DFS       | Rp187.419 |

Greedy lebih ekonomis.

---

## Skenario Krisis

Harga BBM:

Rp20.000/L

| Algoritma |       TCO |
| --------- | --------: |
| Greedy    |  Rp42.293 |
| DFS       | Rp218.604 |

Greedy lebih ekonomis.

---

# 6. Analisis Break-Even Point

Misalkan:

TCO Greedy = TCO DFS

# (2.1145 × P) + 2.795

(2.0790 × P) + 177.023

Selisih konsumsi BBM:

0.0355 liter

Selisih biaya komputasi:

≈ Rp177.020

Maka:

P ≈ Rp4.986.000 per liter

Artinya harga BBM harus mencapai hampir Rp5 juta per liter agar DFS mulai lebih menguntungkan secara finansial.

Nilai tersebut jauh di atas harga pasar realistis.

---

# 7. Kesimpulan Bisnis

Berdasarkan hasil simulasi, DFS Backtracking + Pruning berhasil menghasilkan rute optimal dengan jarak 13.64% lebih pendek dibanding Greedy.

Namun biaya komputasi DFS sangat tinggi akibat eksplorasi 1.774.789 node dan waktu eksekusi sekitar 3.5 detik.

Pada kedua skenario ekonomi yang diuji (subsidi maupun krisis), penghematan BBM yang diperoleh DFS tidak mampu menutupi kenaikan biaya komputasi server.

Oleh karena itu, untuk kondisi operasional perusahaan saat ini, algoritma Greedy Nearest Neighbor merupakan pilihan yang paling rasional secara bisnis karena memberikan Total Cost of Ownership (TCO) paling rendah dengan waktu eksekusi yang sangat cepat.

DFS lebih cocok digunakan untuk kebutuhan analisis offline, validasi kualitas rute, atau dataset dengan jumlah pelanggan yang jauh lebih sedikit.
