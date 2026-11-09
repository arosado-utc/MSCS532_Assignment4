"""
MSCS 532 - Assignment 4
Heap Data Structures: Implementation, Analysis, and Applications

By: Alfredo Rosado
Date: 11-02-26

Heapsort (Part 1) builds a max-heap over the input and then
repeatedly moves the maximum to the end of the array, shrinking the
heap by one element each time. The heap is stored implicitly in the
array: the parent of index i is (i - 1) // 2 and its children are
2i + 1 and 2i + 2.

Part 2 (priority queue and scheduler) lives in priority_queue.py
and scheduler.py.

Based on Chapter 6 of Cormen, Leiserson, Rivest & Stein,
"Introduction to Algorithms" (4th ed., 2022).
"""


def _sift_down(arr, i, size):
    """Restore the max-heap property for the subtree rooted at i.

    The heap holds arr[0..size-1] (elements at index >= size are the
    sorted suffix, outside the heap), and the two children of i are
    assumed to already satisfy the heap property.

    Parameter: arr   - the array acting as the heap
               i     - index of the node to sift down
               size  - number of heap elements
    """
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < size and arr[left] > arr[largest]:
            largest = left
        if right < size and arr[right] > arr[largest]:
            largest = right
        if largest == i:
            return
        arr[i], arr[largest] = arr[largest], arr[i]
        i = largest


def _build_max_heap(arr):
    """Turn arr into a max-heap in place.

    Every node at index n // 2 or higher is a leaf, so sifting down
    from the last internal node (index n // 2 - 1) up to 0 is
    enough. This takes O(n) in total rather than O(n log n): most
    nodes sit near the bottom and only move a little.

    Parameter: arr - the array to convert into a max-heap
    """
    for i in range(len(arr) // 2 - 1, -1, -1):
        _sift_down(arr, i, len(arr))


def heap_sort(arr):
    """Sort a list of comparable elements IN PLACE in increasing order.

    Parameter: arr - list of comparable elements
    Return:    the same list object, sorted in increasing order

    Complexity:
        Time   - O(n log n) in the best, average, and worst case:
                  O(n) to build the heap, then n extractions of the
                  maximum, each O(log n).
        Space  - O(1) extra; the heap lives inside the array and the
                  sift-down is iterative, so there is no recursion.
        Stable - no, because the heap swaps elements freely.
    """
    if len(arr) <= 1:
        return arr
    _build_max_heap(arr)
    for end in range(len(arr) - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(arr, 0, end)
    return arr


def main():
    # A few sample lists to demonstrate the sort
    sample_arrays = [
        [37, 2, 9, 41, 18],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [4, 4, 2, 4, 1],
        [-3, 0, -7, 4, -1],
    ]

    for sample in sample_arrays:
        original = list(sample)
        heap_sort(sample)
        print(f"Before: {original}")
        print(f"After:  {sample}")
        print()


if __name__ == "__main__":
    main()
