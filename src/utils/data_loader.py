import json
import os

def load_routing_data(filepath):
    # Validasi apakah file exist untuk mencegah error path
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File dataset tidak ditemukan di jalur: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Mengekstrak nodes dan matriks ketetanggaan
    nodes = data.get("nodes", [])
    distance_matrix = data.get("distance_matrix", [])
    
    return nodes, distance_matrix

# --- Contoh Penggunaan (Bisa dihapus atau dipindah ke file main.py nanti) ---
if __name__ == "__main__":
    # Path relatif menuju file dataset
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset.json')
    
    try:
        nodes_data, matrix_data = load_routing_data(dataset_path)
        
        print(f"Berhasil memuat {len(nodes_data)} titik (1 Hub & {len(nodes_data)-1} Pelanggan).")
        print(f"Ukuran Matriks Jarak: {len(matrix_data)}x{len(matrix_data[0])}")
        
        # Cek data pelanggan pertama
        print("\nContoh Data Pelanggan 1:")
        print(f"Nama  : {nodes_data[1]['name']}")
        print(f"Berat : {nodes_data[1]['weight_kg']} kg")
        print(f"Jarak Hub ke Pelanggan 1: {matrix_data[0][1]} km")
        
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")