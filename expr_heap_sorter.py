"""
Implementasi ExprHeapSorter
Bab 13: Expression Tree + In-Place HeapSort
"""

from typing import List, Optional
from collections import deque


class ExprHeapSorter:
    def __init__(self, expr_str: str):
        self.expr = expr_str
        self.values: List[int] = []

    # =========================================================
    # 1. EXPRESSION TREE BUILDER & EVALUATOR
    # =========================================================

    def parse_and_evaluate(self) -> List[int]:
        """
        Membangun pohon ekspresi dari string, mengevaluasi hasilnya,
        dan mengembalikan list nilai integer [hasil].
        """
        tokens = deque(self.expr.replace(" ", ""))  # Hapus spasi
        root = self._build_tree(tokens)
        if root is None:
            raise ValueError("Ekspresi kosong atau tidak valid.")
        result = self._eval_tree(root)
        self.values = [result]
        return self.values

    def _build_tree(self, tokens: deque) -> Optional[dict]:
        """
        Membangun pohon ekspresi secara rekursif dari antrian token.

        Pola rekursi (sesuai Listing 13.9):
          - Jika token '(' → buat node internal:
              1. Rekursi untuk subtree kiri
              2. Ambil operator
              3. Rekursi untuk subtree kanan
              4. Konsumsi ')'
          - Jika token adalah digit/angka → buat node leaf

        Node direpresentasikan sebagai dict:
          {'val': operator_atau_angka, 'left': node|None, 'right': node|None}
        """
        if not tokens:
            return None

        token = tokens.popleft()

        if token == '(':
            # Node internal: kiri → operator → kanan
            left = self._build_tree(tokens)

            if not tokens:
                raise ValueError("Ekspresi tidak lengkap: operator tidak ditemukan.")
            operator = tokens.popleft()

            if operator not in ('+', '-', '*', '/'):
                raise ValueError(f"Token tidak valid sebagai operator: '{operator}'")

            right = self._build_tree(tokens)

            if not tokens:
                raise ValueError("Ekspresi tidak lengkap: ')' tidak ditemukan.")
            closing = tokens.popleft()  # Konsumsi ')'
            if closing != ')':
                raise ValueError(f"Diharapkan ')' tetapi mendapat '{closing}'")

            return {'val': operator, 'left': left, 'right': right}

        else:
            # Node leaf: kumpulkan karakter angka (termasuk multi-digit)
            num_str = token
            while tokens and tokens[0].isdigit():
                num_str += tokens.popleft()

            if not num_str.lstrip('-').isdigit():
                raise ValueError(f"Token tidak valid sebagai operand: '{num_str}'")

            return {'val': int(num_str), 'left': None, 'right': None}

    def _eval_tree(self, node: Optional[dict]) -> int:
        """
        Evaluasi pohon ekspresi secara postorder (kiri → kanan → root).
        Mengembalikan nilai integer hasil evaluasi subtree.
        Raises ValueError jika terjadi pembagian nol atau node tidak valid.
        """
        if node is None:
            raise ValueError("Node tidak valid (None).")

        # Node leaf: langsung kembalikan nilai
        if node['left'] is None and node['right'] is None:
            return node['val']

        # Evaluasi subtree kiri dan kanan terlebih dahulu (postorder)
        left_val = self._eval_tree(node['left'])
        right_val = self._eval_tree(node['right'])

        op = node['val']

        if op == '+':
            return left_val + right_val
        elif op == '-':
            return left_val - right_val
        elif op == '*':
            return left_val * right_val
        elif op == '/':
            if right_val == 0:
                raise ValueError(f"Pembagian nol terdeteksi: {left_val} / {right_val}")
            return left_val // right_val  # Integer division
        else:
            raise ValueError(f"Operator tidak dikenal: '{op}'")

    def _postorder_string(self, node: Optional[dict]) -> str:
        """Menghasilkan string notasi postfix dari pohon ekspresi (untuk verifikasi)."""
        if node is None:
            return ""
        if node['left'] is None and node['right'] is None:
            return str(node['val'])
        left_str = self._postorder_string(node['left'])
        right_str = self._postorder_string(node['right'])
        return f"{left_str} {right_str} {node['val']}"

    # =========================================================
    # 2. IN-PLACE HEAPSORT
    # =========================================================

    def heapsort_inplace(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array secara ascending menggunakan In-Place HeapSort.

        Fase 1 — Build max-heap:
          Mulai dari node non-leaf terakhir (n//2 - 1) mundur ke 0.
          sift_down memastikan setiap subtree memenuhi heap order property.
          Kompleksitas: O(n) (analisis amortized).

        Fase 2 — Ekstraksi & penempatan:
          Swap akar (maksimum) dengan elemen terakhir heap.
          Kurangi heap_size, lalu sift_down dari indeks 0.
          Ulangi hingga heap_size = 1.
          Kompleksitas: O(n log n).

        Total ruang tambahan: O(1) — hanya variabel indeks.
        """
        n = len(arr)
        if n <= 1:
            return arr

        # Fase 1: Bangun max-heap in-place (bottom-up)
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(arr, n, i)

        # Fase 2: Ekstraksi elemen maksimum satu per satu
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]   # Pindahkan max ke akhir
            self._sift_down(arr, end, 0)           # Pulihkan heap untuk heap_size = end

        return arr

    def _sift_down(self, arr: List[int], heap_size: int, idx: int):
        """
        Memulihkan heap order property dengan mendorong elemen ke bawah.

        Algoritma:
          1. Hitung indeks anak kiri dan kanan.
          2. Temukan indeks terbesar di antara parent, kiri, kanan.
          3. Jika terbesar bukan parent, swap dan lanjutkan dari posisi baru.
          4. Berhenti jika parent sudah terbesar atau mencapai leaf.

        Rumus indeks:
          left  = 2 * idx + 1
          right = 2 * idx + 2

        Jumlah perbandingan maksimum: 2 * log2(heap_size) = O(log n).
        """
        while True:
            largest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2

            # Bandingkan dengan anak kiri
            if left < heap_size and arr[left] > arr[largest]:
                largest = left

            # Bandingkan dengan anak kanan
            if right < heap_size and arr[right] > arr[largest]:
                largest = right

            # Jika parent sudah terbesar, heap order property terpenuhi
            if largest == idx:
                break

            # Swap dan lanjutkan dari posisi baru
            arr[idx], arr[largest] = arr[largest], arr[idx]
            idx = largest

    # =========================================================
    # 3. COMPLETE TREE VALIDATOR
    # =========================================================

    def is_complete_tree(self, arr: List[int]) -> bool:
        """
        Memvalidasi apakah array memenuhi properti complete binary tree.

        Complete binary tree: semua level terisi penuh kecuali level terakhir,
        dan level terakhir diisi dari kiri ke kanan tanpa celah.

        Pada representasi array, ini berarti:
          - Untuk setiap indeks i dari 0 sampai n-1,
            jika anak kiri (2i+1) atau anak kanan (2i+2) ada di array,
            maka tidak boleh ada "lubang" (indeks yang loncat).
          - Jika ditemukan indeks i yang tidak ada (i >= n) tetapi ada
            indeks j > i yang terisi, itu bukan complete tree.

        Strategi: BFS-style check — setelah menemukan node pertama yang
        tidak punya anak lengkap, semua node berikutnya harus leaf.
        """
        n = len(arr)
        if n == 0:
            return True

        found_non_full = False  # Sudah ditemukan node dengan anak tidak lengkap?

        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2

            left_exists = left < n
            right_exists = right < n

            if right_exists and not left_exists:
                # Anak kanan ada tapi kiri tidak — mustahil pada complete tree
                return False

            if found_non_full:
                # Setelah node tidak penuh, semua node harus leaf
                if left_exists or right_exists:
                    return False
            else:
                if not right_exists:
                    # Node ini tidak punya anak kanan → catat, semua berikutnya harus leaf
                    found_non_full = True

        return True


# =========================================================
# DEMO & TEST
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("   DEMO ExprHeapSorter")
    print("=" * 60)

    # --- Test 1: Expression Tree ---
    print("\n[1] Expression Tree Builder & Evaluator")

    expressions = [
        "((8*5)+(9/(7-4)))",    # Dari soal: (8*5) + (9/(7-4)) = 40 + 3 = 43
        "((3+4)*(2-1))",         # (3+4)*(2-1) = 7*1 = 7
        "((10/2)+(3*4))",        # (10/2)+(3*4) = 5+12 = 17
    ]

    for expr in expressions:
        sorter = ExprHeapSorter(expr)
        try:
            tokens_check = deque(expr.replace(" ", ""))
            root = sorter._build_tree(tokens_check)
            postfix = sorter._postorder_string(root)
            result = sorter.parse_and_evaluate()
            print(f"\n  Ekspresi  : {expr}")
            print(f"  Postfix   : {postfix}")
            print(f"  Hasil eval: {result[0]}")
        except ValueError as e:
            print(f"  Error: {e}")

    # Test pembagian nol
    print("\n  Test pembagian nol: ((5/(3-3))+1)")
    try:
        s = ExprHeapSorter("((5/(3-3))+1)")
        s.parse_and_evaluate()
    except ValueError as e:
        print(f"  Tertangkap ValueError: {e}")

    # --- Test 2: In-Place HeapSort ---
    print("\n[2] In-Place HeapSort")
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 5, 5, 5],                   # Semua sama
        [1],                             # Satu elemen
        [],                              # Kosong
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3], # Duplikat
        list(range(10, 0, -1)),          # Descending worst-case
    ]

    sorter = ExprHeapSorter("")
    for tc in test_cases:
        arr_copy = tc[:]
        result = sorter.heapsort_inplace(tc[:])
        print(f"  Input : {arr_copy}")
        print(f"  Output: {result}\n")

    # --- Test 3: Complete Tree Validator ---
    print("[3] Complete Tree Validator")
    arrays = [
        ([1, 2, 3, 4, 5, 6, 7], True,  "Sempurna (7 node, 3 level)"),
        ([1, 2, 3, 4, 5, 6],    True,  "Complete (6 node, level terakhir tidak penuh)"),
        ([1, 2, 3, 4, 5],       True,  "Complete (5 node)"),
        ([1, 2, 3, 4],          True,  "Complete (4 node)"),
        ([1],                   True,  "Single node"),
        ([],                    True,  "Kosong"),
    ]

    for arr, expected, desc in arrays:
        result = sorter.is_complete_tree(arr)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {desc}: {arr} → {result}")

    print("\n" + "=" * 60)
    print("  Semua test selesai.")
    print("=" * 60)
