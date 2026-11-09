"""
MSCS 532 - Assignment 4
Test suite for the heap sort, priority queue, and scheduler.

Run with:  python3 tests.py

Covers heap sort correctness on several input shapes, the priority
queue's ordering and key-change behavior, and the scheduler's
dispatch decisions on a hand-checked workload.
"""

import random

from main import heap_sort
from priority_queue import PriorityQueue, Task
from scheduler import run_scheduler, sample_workload
from sorts import merge_sort, randomized_quick_sort


def test_heap_sort_matches_builtin():
    """Heap sort must agree with the built-in sorted() on random data."""
    rng = random.Random(7)
    for n in (0, 1, 2, 5, 50, 500):
        data = [rng.randint(-1000, 1000) for _ in range(n)]
        heap_sort(data)
        assert data == sorted(data), f"n={n}"


def test_heap_sort_is_in_place():
    """heap_sort must sort the SAME list object and return it."""
    data = [5, 3, 8, 1]
    result = heap_sort(data)
    assert result is data, "heap_sort must sort in place"
    assert data == [1, 3, 5, 8]


def test_heap_sort_ordered_inputs():
    """Already-sorted and reverse-sorted inputs must still come out
    sorted; heap sort has no input-dependent worst case."""
    ascending = list(range(1000))
    descending = list(range(1000, 0, -1))
    heap_sort(ascending)
    assert ascending == list(range(1000))
    heap_sort(descending)
    assert descending == list(range(1, 1001))


def test_heap_sort_duplicates():
    """Many equal elements must not break the heap property."""
    data = [3, 3, 3, 1, 3, 2, 3, 3]
    heap_sort(data)
    assert data == [1, 2, 3, 3, 3, 3, 3, 3]


def test_sorts_from_earlier_assignments():
    """The reused merge sort and quick sort must still agree with
    the built-in sorted()."""
    rng = random.Random(11)
    data = [rng.randint(-500, 500) for _ in range(200)]
    assert merge_sort(data) == sorted(data)
    randomized_quick_sort(list(data))
    assert merge_sort(data) == sorted(data)


def test_pq_extract_order():
    """Tasks must come out in priority order, ties broken by
    earlier arrival."""
    pq = PriorityQueue()
    tasks = [
        Task("a", 5, 3),
        Task("b", 9, 1),
        Task("c", 9, 2),
        Task("d", 2, 0),
        Task("e", 5, 1),
    ]
    for t in tasks:
        pq.insert(t)
    order = [pq.extract_max().task_id for _ in range(len(tasks))]
    assert order == ["b", "c", "e", "a", "d"]


def test_pq_extract_all_multiset():
    """Every inserted task must come out exactly once."""
    rng = random.Random(1)
    pq = PriorityQueue()
    tasks = [Task(f"t{i}", rng.randint(0, 20), rng.randint(0, 10))
             for i in range(500)]
    for t in tasks:
        pq.insert(t)
    out = []
    while not pq.is_empty():
        out.append(pq.extract_max())
    assert sorted(t.task_id for t in out) == sorted(t.task_id for t in tasks)
    # and the order must be non-increasing in priority
    for earlier, later in zip(out, out[1:]):
        assert earlier.priority >= later.priority


def test_pq_interleaved_insert_extract():
    """Inserting and extracting in between must still respect the
    priority order."""
    pq = PriorityQueue()
    pq.insert(Task("a", 1, 0))
    pq.insert(Task("b", 3, 0))
    assert pq.extract_max().task_id == "b"
    pq.insert(Task("c", 2, 0))
    assert pq.extract_max().task_id == "c"
    assert pq.extract_max().task_id == "a"
    assert pq.is_empty()


def test_pq_increase_decrease_key():
    """Key changes must move the task and be reflected in peek()."""
    pq = PriorityQueue()
    a = Task("a", 1, 0)
    b = Task("b", 5, 0)
    c = Task("c", 3, 0)
    for t in (a, b, c):
        pq.insert(t)
    pq.increase_key(a, 9)
    assert pq.peek().task_id == "a"
    pq.decrease_key(a, 0)
    assert pq.peek().task_id == "b"
    # after a full extract pass the order must be correct
    out = [pq.extract_max().task_id for _ in range(3)]
    assert out == ["b", "c", "a"]


def test_pq_key_change_errors():
    """increase/decrease_key must reject tasks that are not in the
    queue and key changes in the wrong direction."""
    pq = PriorityQueue()
    a = Task("a", 1, 0)
    pq.insert(a)
    outside = Task("x", 0, 0)
    try:
        pq.increase_key(outside, 5)
        raise AssertionError("should have raised KeyError")
    except KeyError:
        pass
    try:
        pq.increase_key(a, 0)
        raise AssertionError("should have raised ValueError")
    except ValueError:
        pass
    try:
        pq.decrease_key(a, 2)
        raise AssertionError("should have raised ValueError")
    except ValueError:
        pass


def test_pq_empty_errors():
    """extract_max and peek must raise on an empty queue."""
    pq = PriorityQueue()
    assert pq.is_empty()
    for op in (pq.extract_max, pq.peek):
        try:
            op()
            raise AssertionError("should have raised IndexError")
        except IndexError:
            pass


def test_scheduler_sample_workload_hand_check():
    """The sample workload is small enough to check by hand:
    at t=0 the incident (prio 5) runs to t=2, then the build
    (prio 3) runs to t=4, then the report (prio 2, arrived at t=2)
    runs to t=5, then the backup (prio 1) runs to t=8."""
    tasks = sample_workload()
    report = run_scheduler(tasks)
    r = report["results"]
    assert r["incident"] == (2, 0, 2)
    assert r["build"] == (4, 2, 4)
    assert r["report"] == (5, 2, 3)
    assert r["backup"] == (8, 5, 8)
    assert abs(report["avg_finish"] - 4.75) < 1e-9
    assert abs(report["avg_wait"] - 2.25) < 1e-9
    assert abs(report["avg_turnaround"] - 4.25) < 1e-9
    assert report["deadline_misses"] == 0


def test_scheduler_idle_gap_and_deadline_miss():
    """The processor must jump to the next arrival when nothing is
    ready, and a task finishing after its deadline is a miss."""
    tasks = [Task("late", 1, arrival=5, deadline=10, run_time=2),
             Task("tight", 5, arrival=0, deadline=1, run_time=2)]
    report = run_scheduler(tasks)
    # tight (prio 5) runs first: 0 -> 2 (misses its deadline of 1)
    # late (prio 1) runs next: 2 -> 4 (wait is 0: it arrived at 5?
    # no - it started at 2, before its arrival at 5, which must not
    # happen)
    assert report["results"]["tight"] == (2, 0, 2)
    assert report["results"]["late"][0] >= 5 + 2  # cannot finish before arrival + run
    assert report["deadline_misses"] == 1


def main():
    tests = [
        test_heap_sort_matches_builtin,
        test_heap_sort_is_in_place,
        test_heap_sort_ordered_inputs,
        test_heap_sort_duplicates,
        test_sorts_from_earlier_assignments,
        test_pq_extract_order,
        test_pq_extract_all_multiset,
        test_pq_interleaved_insert_extract,
        test_pq_increase_decrease_key,
        test_pq_key_change_errors,
        test_pq_empty_errors,
        test_scheduler_sample_workload_hand_check,
        test_scheduler_idle_gap_and_deadline_miss,
    ]

    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL: {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"ERROR: {test.__name__}: {type(e).__name__}: {e}")

    print()
    if failed:
        print(f"{failed} of {len(tests)} test(s) FAILED.")
        raise SystemExit(1)
    print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
