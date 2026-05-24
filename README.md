# 📦 Tugas Analisis & Desain Algoritma
## Sorting Lanjutan + Binary Tree & HeapSort

Repositori ini berisi **jawaban teori lengkap** dan **implementasi kode** untuk dua bagian tugas: algoritma sorting lanjutan (Bab 12) dan pohon ekspresi + heapsort (Bab 13).

---

## 📁 Struktur File

```
├── advanced_sorter.py      # Implementasi AdvancedSorter (Bab 12)
├── expr_heap_sorter.py     # Implementasi ExprHeapSorter (Bab 13)
├── teori_jawaban.md        # Jawaban seluruh pertanyaan teori (8 soal)
└── README.md
```

---

## ⚙️ Cara Menjalankan

```bash
python3 advanced_sorter.py
python3 expr_heap_sorter.py
```

Tidak ada dependensi eksternal — hanya Python 3 standar.

---

# BAGIAN 1 — Sorting Lanjutan (`advanced_sorter.py`)

## Deskripsi Modul

Kelas `AdvancedSorter` mengimplementasikan tiga algoritma sorting dengan batasan ketat:

| Fitur | Ketentuan | Status |
|---|---|---|
| `list.sort()` / `sorted()` | ❌ Dilarang | ✅ Tidak digunakan |
| Slice `[:]` untuk pemisahan | ❌ Dilarang | ✅ Tidak digunakan |
| Alokasi node baru saat sorting LL | ❌ Dilarang | ✅ Hanya modifikasi `.next` |
| Stabilitas urutan | ✅ Wajib untuk Merge Sort | ✅ Dijaga via `<=` |
| Quick Sort fallback | ✅ Wajib jika depth > 2·log₂n | ✅ Beralih ke `sort_array` |

---

## 1. Array Merge Sort — `sort_array()`

### Cara Kerja

Menggunakan **virtual sublists** — subarray tidak pernah disalin secara fisik. Hanya satu `tmpArray` berukuran n yang dialokasikan di awal, dipakai ulang di setiap level rekursi.

```
sort_array([38, 27, 43, 3, 9, 82, 10])
              ↓
  _rec_merge_sort(arr, 0, 6, tmp)
      _rec_merge_sort(arr, 0, 3, tmp)   ← kiri
      _rec_merge_sort(arr, 4, 6, tmp)   ← kanan
      _merge_virtual(arr, 0, 3, 6, tmp) ← gabung
              ↓
  [3, 9, 10, 27, 38, 43, 82]
```

### Stabilitas

Kondisi `arr[a] <= arr[b]` di `_merge_virtual()` memastikan elemen kiri diambil lebih dulu jika nilainya sama → urutan relatif asli dipertahankan.

### Kompleksitas

| | Nilai |
|---|---|
| Waktu | O(n log n) |
| Ruang tambahan | O(n) — satu tmpArray |
| Stack rekursi | O(log n) |

---

## 2. Linked List Merge Sort — `sort_linked_list()`

### Cara Kerja

**`_split_linked_list()` — Fast-Slow Pointer**

```
List: 1 → 2 → 3 → 4 → 5 → None

Inisialisasi:
  midPoint (slow) = node(1)
  curNode  (fast) = node(2)

Iterasi 1: slow → node(2), fast → node(4)
Iterasi 2: slow → node(3), fast → None  ← berhenti

right_head = node(4)
midPoint.next = None  →  kiri: 1→2→3,  kanan: 4→5
```

Satu traversal, tanpa menghitung panjang list.

**`_merge_linked_lists()` — Dummy Node + Tail Reference**

```python
dummy = ListNode(0)   # Anchor tetap
tail = dummy

# Selama merge: tail.next = node_terpilih, tail = tail.next
# Hanya pengalihan pointer, TIDAK ada node baru

return dummy.next     # Lewati sentinel
```

### Kompleksitas

| | Nilai |
|---|---|
| Waktu | O(n log n) |
| Ruang heap | O(1) per merge (1 dummy node) |
| Stack rekursi | O(log n) |

---

## 3. Quick Sort — `quick_sort()` + `partition_quick()`

### Strategi Pivot: Median-of-Three

Memilih median dari `arr[first]`, `arr[mid]`, `arr[last]` sebagai pivot.
Mencegah worst-case O(n²) pada data terurut/terbalik karena pivot tidak lagi selalu elemen terkecil atau terbesar.

### Depth Limiter (Fallback ke Merge Sort)

```python
if depth > 2 * log2(n):
    # Beralih ke sort_array() untuk subarray ini
```

Jika rekursi terlalu dalam, otomatis beralih ke Merge Sort O(n log n) yang terjamin.

### Kompleksitas

| Kasus | Waktu |
|---|---|
| Rata-rata | O(n log n) |
| Terburuk (dengan fallback) | O(n log n) — dijamin |
| Tanpa fallback, pivot buruk | O(n²) |

---

# BAGIAN 2 — Binary Tree & HeapSort (`expr_heap_sorter.py`)

## Deskripsi Modul

Kelas `ExprHeapSorter` menggabungkan tiga modul Bab 13 menjadi satu pipeline:

```
String ekspresi  →  Expression Tree  →  Evaluasi  →  HeapSort  →  Array terurut
```

---

## 1. Expression Tree Builder — `_build_tree()`

### Cara Kerja Rekursif

Menerima `deque` token dan membangun pohon dengan pola:

```
Token '(' → buat node internal:
    1. rekursi → subtree kiri
    2. ambil operator (+, -, *, /)
    3. rekursi → subtree kanan
    4. konsumsi ')'

Token digit → buat node leaf langsung
```

### Contoh: `((8*5)+(9/(7-4)))`

```
          +
        /   \
       *     /
      / \   / \
     8   5 9   -
              / \
             7   4

Postfix: 8 5 * 9 7 4 - / +
Hasil  : (8×5) + (9÷(7-4)) = 40 + 3 = 43
```

Traversal **postorder** (kiri → kanan → root) menghasilkan notasi postfix secara otomatis tanpa tanda kurung tambahan.

### Penanganan Error

| Kondisi | Exception |
|---|---|
| Pembagian nol | `ValueError: Pembagian nol terdeteksi` |
| Token tidak valid | `ValueError: Token tidak valid` |
| Ekspresi tidak lengkap | `ValueError: Ekspresi tidak lengkap` |

---

## 2. In-Place HeapSort — `heapsort_inplace()`

### Dua Fase

**Fase 1 — Build Max-Heap O(n)**
```
Mulai dari node non-leaf terakhir (n//2 - 1) mundur ke 0.
Setiap sift_down memastikan subtree memenuhi heap order property.

[64, 34, 25, 12, 22, 11, 90]  →  [90, 34, 64, 12, 22, 11, 25]
```

**Fase 2 — Ekstraksi O(n log n)**
```
Swap arr[0]↔arr[n-1], kurangi heap_size, sift_down dari 0.
Ulangi hingga heap_size = 1.

Hasil: [11, 12, 22, 25, 34, 64, 90]  ← ascending
```

### Kompleksitas

| | Nilai |
|---|---|
| Waktu | O(n log n) |
| Ruang tambahan | **O(1)** — hanya variabel indeks |
| Stabilitas | Tidak stabil (inheren pada heapsort) |

---

## 3. Complete Tree Validator — `is_complete_tree()`

Memvalidasi apakah array memenuhi properti complete binary tree (diisi level-by-level kiri ke kanan tanpa celah).

```
[1, 2, 3, 4, 5, 6, 7]  →  True  (pohon sempurna)
[1, 2, 3, 4, 5, 6]     →  True  (level terakhir dari kiri)
```

---

## 🔑 Ringkasan Teknik Utama

| Teknik | Digunakan di | Manfaat |
|---|---|---|
| Virtual sublists + single tmpArray | `_merge_virtual()` | Ruang O(n), bukan O(n log n) |
| Fast-slow pointer | `_split_linked_list()` | Titik tengah dalam satu traversal |
| Dummy node + tail reference | `_merge_linked_lists()` | Merge tanpa alokasi node baru |
| Median-of-Three pivot | `partition_quick()` | Hindari O(n²) pada data terurut |
| Depth limiter + Merge Sort fallback | `_quick_sort_recursive()` | Garansi O(n log n) worst-case |
| Pohon ekspresi rekursif | `_build_tree()` | Parse ekspresi bersarang tanpa regex |
| Bottom-up build heap | `heapsort_inplace()` | Build O(n) lebih efisien |
| Iterative sift-down | `_sift_down()` | O(1) ruang, hindari rekursi dalam |

---

## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/KaivalAmamiya/Tugas-Struktur-Data-Sorting-Binary-Tree.git
cd Tugas-Struktur-Data-Sorting-Binary-Tree
```

---

## 👤 Informasi

> Tugas Analisis & Desain Algoritma
> Topik: Sorting Lanjutan (Bab 12) + Binary Tree & HeapSort (Bab 13)
