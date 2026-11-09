"""
MSCS 532 - Assignment 4
Sorting algorithms reused from earlier assignments for the
comparison in benchmark.py:

  merge_sort            - Assignment 2 (divide and conquer, stable)
  randomized_quick_sort - Assignment 3 (random pivot, in place)

Both are copied as-is from their respective repositories so this
repository is self-contained.
"""

import random


# ---------------------------------------------------------------------
# Merge sort (from Assignment 2, main.py)
# ---------------------------------------------------------------------

def merge_sort(arr):
    """Sort a list of comparable elements in increasing order.

    Parameter: arr - list of comparable elements
    Return:    a NEW list containing arr sorted in increasing order
    """
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(left, right):
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ---------------------------------------------------------------------
# Randomized quick sort (from Assignment 3, main.py)
# ---------------------------------------------------------------------

def partition(arr, low, high, pivot_index):
    """Lomuto partition around the element at pivot_index."""
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
    pivot = arr[high]
    i = low - 1  # index of the last element known to be <= pivot
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def _quicksort(arr, low, high):
    """Recursive driver for randomized_quick_sort; bounds are inclusive."""
    if low >= high:
        return
    pivot_index = random.randint(low, high)
    p = partition(arr, low, high, pivot_index)
    _quicksort(arr, low, p - 1)
    _quicksort(arr, p + 1, high)


def randomized_quick_sort(arr):
    """Sort a list of comparable elements IN PLACE in increasing order.

    Parameter: arr - list of comparable elements
    Return:    the same list object, sorted in increasing order
    """
    if not arr:
        return arr
    _quicksort(arr, 0, len(arr) - 1)
    return arr
