"""
Implementasi AdvancedSorter
Bab 12: Sorting Lanjutan — Array Merge Sort, Linked List Merge Sort, Quick Sort
"""

import math
from typing import List, Optional


class ListNode:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

    def __repr__(self):
        return f"ListNode({self.data})"


class AdvancedSorter:
    def __init__(self):
        pass

    # =========================================================
    # 1. ARRAY MERGE SORT (Virtual Sublists + Single tmpArray)
    # =========================================================

    def sort_array(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array secara ascending menggunakan Merge Sort.
        Hanya mengalokasikan SATU tmpArray di awal — O(n) ruang tambahan.
        Tidak ada slice atau subarray fisik di rekursi.
        """
        if len(arr) <= 1:
            return arr
        tmp_array = [0] * len(arr)  # Satu-satunya alokasi tambahan
        self._rec_merge_sort(arr, 0, len(arr) - 1, tmp_array)
        return arr

    def _rec_merge_sort(self, arr, first, last, tmp_array):
        """Rekursi pembagi: bagi array menjadi dua virtual sublist secara rekursif."""
        if first >= last:
            return
        mid = (first + last) // 2
        self._rec_merge_sort(arr, first, mid, tmp_array)
        self._rec_merge_sort(arr, mid + 1, last, tmp_array)
        self._merge_virtual(arr, first, mid, last, tmp_array)

    def _merge_virtual(self, arr, left_start, mid, right_end, tmp_array):
        """
        Gabungkan dua virtual sublist yang bersebelahan:
          - Sublist kiri : arr[left_start .. mid]
          - Sublist kanan: arr[mid+1 .. right_end]

        Stabilitas dijaga dengan kondisi '<=' saat perbandingan:
        jika elemen kiri <= elemen kanan, ambil dari kiri terlebih dahulu.
        Hasilnya disimpan sementara di tmp_array lalu disalin kembali ke arr.
        """
        a = left_start       # Pointer sublist kiri
        b = mid + 1          # Pointer sublist kanan
        k = left_start       # Pointer tmp_array

        while a <= mid and b <= right_end:
            if arr[a] <= arr[b]:   # <= untuk stabilitas: kiri diutamakan jika sama
                tmp_array[k] = arr[a]
                a += 1
            else:
                tmp_array[k] = arr[b]
                b += 1
            k += 1

        # Salin sisa sublist kiri (jika ada)
        while a <= mid:
            tmp_array[k] = arr[a]
            a += 1
            k += 1

        # Salin sisa sublist kanan (jika ada)
        while b <= right_end:
            tmp_array[k] = arr[b]
            b += 1
            k += 1

        # Salin kembali dari tmp_array ke arr (hanya segmen yang diproses)
        for i in range(left_start, right_end + 1):
            arr[i] = tmp_array[i]

    # =========================================================
    # 2. LINKED LIST MERGE SORT (Fast-Slow + Dummy Merge)
    # =========================================================

    def sort_linked_list(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Mengurutkan singly linked list menggunakan Merge Sort.
        Hanya memodifikasi pointer .next — tidak mengalokasikan node baru.
        Kompleksitas ruang: O(log n) untuk stack rekursi.
        """
        if head is None or head.next is None:
            return head

        # Pisah list menjadi dua bagian menggunakan fast-slow pointer
        right_head = self._split_linked_list(head)
        left_head = head

        # Rekursi untuk mengurutkan masing-masing bagian
        left_sorted = self.sort_linked_list(left_head)
        right_sorted = self.sort_linked_list(right_head)

        # Gabungkan dua list terurut
        return self._merge_linked_lists(left_sorted, right_sorted)

    def _split_linked_list(self, head: ListNode) -> Optional[ListNode]:
        """
        Menemukan titik tengah list dalam SATU traversal menggunakan
        teknik fast-slow pointer (Floyd's tortoise and hare):
          - midPoint (slow): bergerak 1 langkah per iterasi
          - curNode  (fast): bergerak 2 langkah per iterasi

        Ketika curNode mencapai akhir, midPoint tepat di tengah.
        Putus link di midPoint.next = None, kembalikan head sublist kanan.
        """
        midPoint = head          # Slow pointer
        curNode = head.next      # Fast pointer (mulai dari head.next agar split seimbang)

        while curNode is not None and curNode.next is not None:
            midPoint = midPoint.next       # Maju 1
            curNode = curNode.next.next    # Maju 2

        right_head = midPoint.next   # Kepala sublist kanan
        midPoint.next = None         # Putus koneksi → sublist kiri berakhir di midPoint

        return right_head

    def _merge_linked_lists(self, listA: Optional[ListNode], listB: Optional[ListNode]) -> Optional[ListNode]:
        """
        Menggabungkan dua linked list terurut secara STABLE menggunakan:
          - dummy node: sentinel tetap sebagai anchor hasil merge
          - tail reference: selalu menunjuk node terakhir yang ditambahkan

        Tidak ada alokasi node baru selama merge — hanya pengalihan pointer .next.
        dummy node dibuat sekali per panggilan (O(1) per merge).
        """
        dummy = ListNode(0)   # Sentinel node — tidak masuk ke hasil akhir
        tail = dummy           # tail selalu menunjuk node terakhir yang ditambahkan

        while listA is not None and listB is not None:
            if listA.data <= listB.data:   # <= untuk stabilitas
                tail.next = listA
                listA = listA.next
            else:
                tail.next = listB
                listB = listB.next
            tail = tail.next

        # Sambungkan sisa list yang belum habis
        tail.next = listA if listA is not None else listB

        return dummy.next   # Lewati dummy node

    # =========================================================
    # 3. QUICK SORT (Median-of-Three Pivot + Depth Fallback)
    # =========================================================

    def quick_sort(self, arr: List[int]) -> List[int]:
        """Entry point Quick Sort dengan fallback ke Merge Sort jika rekursi terlalu dalam."""
        if len(arr) <= 1:
            return arr
        limit = int(2 * math.log2(len(arr))) if len(arr) > 1 else 1
        self._quick_sort_recursive(arr, 0, len(arr) - 1, depth=0, limit=limit)
        return arr

    def _quick_sort_recursive(self, arr, first, last, depth, limit):
        """
        Rekursi Quick Sort dengan Depth Limiter.
        Jika kedalaman rekursi melebihi 2*log2(n), beralih ke Merge Sort
        untuk menghindari degradasi O(n²) pada data patologis.
        """
        if first >= last:
            return

        # Fallback ke Merge Sort jika kedalaman berlebihan
        if depth > limit:
            sub = arr[first:last + 1]
            self.sort_array(sub)
            arr[first:last + 1] = sub
            return

        pivot_pos = self.partition_quick(arr, first, last)
        self._quick_sort_recursive(arr, first, pivot_pos - 1, depth + 1, limit)
        self._quick_sort_recursive(arr, pivot_pos + 1, last, depth + 1, limit)

    def partition_quick(self, arr: List[int], first: int, last: int) -> int:
        """
        Partisi dengan strategi pivot Median-of-Three:
          1. Hitung mid = (first + last) // 2
          2. Urutkan arr[first], arr[mid], arr[last] sehingga median berada di arr[first]
          3. Jalankan partisi standar (Lomuto-style) dengan pivot = arr[first]

        Median-of-Three mencegah worst-case O(n²) pada data terurut/terbalik.

        Catatan stabilitas: partisi in-place Quick Sort secara inheren TIDAK stabil
        karena swap jarak jauh dapat mengubah urutan relatif elemen bernilai sama.
        Stabilitas dijaga di level Merge Sort (sort_array & sort_linked_list).
        """
        mid = (first + last) // 2

        # Urutkan arr[first], arr[mid], arr[last] → median ke arr[first]
        if arr[mid] < arr[first]:
            arr[first], arr[mid] = arr[mid], arr[first]
        if arr[last] < arr[first]:
            arr[first], arr[last] = arr[last], arr[first]
        if arr[mid] < arr[last]:
            arr[last], arr[mid] = arr[mid], arr[last]
        # Sekarang: arr[first] <= arr[last] <= arr[mid]
        # Median berada di arr[last] → tukar ke arr[first] sebagai pivot
        arr[first], arr[last] = arr[last], arr[first]

        pivot = arr[first]
        left = first + 1
        right = last

        while True:
            # Geser left ke kanan selama elemen <= pivot
            while left <= right and arr[left] <= pivot:
                left += 1
            # Geser right ke kiri selama elemen > pivot
            while left <= right and arr[right] > pivot:
                right -= 1

            if left > right:
                break

            arr[left], arr[right] = arr[right], arr[left]
            left += 1
            right -= 1

        # Tempatkan pivot ke posisi finalnya
        arr[first], arr[right] = arr[right], arr[first]
        return right   # Posisi akhir pivot


# =========================================================
# UTILITAS: Konversi linked list ↔ Python list
# =========================================================

def list_to_linked(lst):
    """Buat linked list dari Python list."""
    if not lst:
        return None
    head = ListNode(lst[0])
    cur = head
    for val in lst[1:]:
        cur.next = ListNode(val)
        cur = cur.next
    return head


def linked_to_list(head):
    """Konversi linked list ke Python list."""
    result = []
    while head:
        result.append(head.data)
        head = head.next
    return result


# =========================================================
# DEMO & TEST
# =========================================================

if __name__ == "__main__":
    sorter = AdvancedSorter()

    print("=" * 55)
    print("   DEMO AdvancedSorter")
    print("=" * 55)

    # --- Test 1: Array Merge Sort ---
    print("\n[1] Array Merge Sort (Virtual Sublists + Single tmpArray)")
    arr1 = [38, 27, 43, 3, 9, 82, 10]
    print(f"  Input  : {arr1}")
    result1 = sorter.sort_array(arr1[:])
    print(f"  Output : {result1}")

    # Test stabilitas: elemen duplikat
    arr2 = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    print(f"\n  Input  (duplikat): {arr2}")
    result2 = sorter.sort_array(arr2[:])
    print(f"  Output (stabil)  : {result2}")

    # --- Test 2: Linked List Merge Sort ---
    print("\n[2] Linked List Merge Sort (Fast-Slow + Dummy Node)")
    data_ll = [64, 34, 25, 12, 22, 11, 90]
    head = list_to_linked(data_ll)
    print(f"  Input  : {data_ll}")
    sorted_head = sorter.sort_linked_list(head)
    print(f"  Output : {linked_to_list(sorted_head)}")

    # Test stabilitas linked list
    data_ll2 = [5, 3, 5, 1, 3, 2]
    head2 = list_to_linked(data_ll2)
    print(f"\n  Input  (duplikat): {data_ll2}")
    sorted_head2 = sorter.sort_linked_list(head2)
    print(f"  Output (stabil)  : {linked_to_list(sorted_head2)}")

    # --- Test 3: Quick Sort ---
    print("\n[3] Quick Sort (Median-of-Three + Depth Fallback)")
    arr3 = [10, 7, 8, 9, 1, 5]
    print(f"  Input  (acak)      : {arr3}")
    result3 = sorter.quick_sort(arr3[:])
    print(f"  Output             : {result3}")

    # Worst-case tanpa fallback: descending
    arr4 = list(range(20, 0, -1))
    print(f"\n  Input  (descending): {arr4}")
    result4 = sorter.quick_sort(arr4[:])
    print(f"  Output (w/ fallback): {result4}")

    print("\n" + "=" * 55)
    print("  Semua test selesai.")
    print("=" * 55)
