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

TODO: implement heap sort.
"""


def heap_sort(arr):
    """Sort a list of comparable elements IN PLACE in increasing order.

    TODO: implement heap sort (build a max-heap over arr, then
    repeatedly swap the maximum to the end and restore the heap on
    the remaining prefix).
    """
    # Placeholder - the algorithm is not implemented yet.
    return arr


def main():
    # A few sample lists to demonstrate the sort
    sample_arrays = [
        [12, 11, 13, 5, 6],
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
