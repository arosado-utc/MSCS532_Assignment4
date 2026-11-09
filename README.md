# Assignment 4: Heap Data Structures — Implementation, Analysis, and Applications

In this assignment I implemented heap sort on an array-based binary
max-heap and compared it empirically with merge sort and randomized
quick sort. For Part 2 I built a priority queue on the same heap with
a `Task` class and used it in a non-preemptive task-scheduling
simulation.

Reference: Cormen, Leiserson, Rivest & Stein, *Introduction to
Algorithms* (4th ed., 2022), Chapter 6.

## Running the code

Python 3.8 or higher; matplotlib only if you want to regenerate the
plots.

```bash
python3 main.py             # heap sort demo
python3 priority_queue.py   # priority queue demo
python3 scheduler.py        # scheduling simulation
python3 tests.py            # test suite (13 tests)
python3 benchmark.py        # rewrites results/benchmark_results.csv and plots/
```

## What is in the repo

| File                | Description                                            |
| ------------------- | ------------------------------------------------------ |
| `main.py`           | Heap sort + a small demo                               |
| `priority_queue.py` | `Task` class + binary max-heap priority queue + demo   |
| `scheduler.py`      | Non-preemptive priority scheduler simulation           |
| `sorts.py`          | Merge sort (Assignment 2) and quick sort (Assignment 3) |
| `benchmark.py`      | Benchmark harness (wall time + peak memory, CSV + plots) |
| `tests.py`          | Test suite covering all three parts                    |
| `results/`          | `benchmark_results.csv` — the measured data            |
| `plots/`            | Log-log comparison plots generated from the CSV        |

## Heapsort

### Implementation

The input array is treated as a complete binary tree: the parent of
index `i` is `(i - 1) // 2`, and its children are `2i + 1` and `2i + 2`.
There are two phases:

1. **Build the max-heap** in place: sift down from the last internal
   node (`n // 2 - 1`) up to the root.
2. **Extract the maximum** `n - 1` times: swap the root (the maximum)
   with the last heap element, shrink the heap by one, and sift the
   new root down.

```python
def heap_sort(arr):
    _build_max_heap(arr)
    for end in range(len(arr) - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        _sift_down(arr, 0, end)
    return arr
```

The heap lives inside the input array and `_sift_down` is iterative,
so the extra space is O(1) — no recursion stack and no auxiliary
arrays.

### The complexity argument

The interesting thing about heap sort is that its cost does not depend
on the input order at all: the array always forms a complete binary
tree of height `floor(log2 n)`, so every sift-down costs O(log n)
regardless of what the data is. The bound has two parts.

- **Building the heap is O(n), not O(n log n).** At most
  `n / 2^(h+1)` nodes have height `h`, and sifting one of them down
  costs O(h), so the total cost is
  `sum_h (n / 2^(h+1)) * (h + 1)`, which is O(n): the series
  `sum h / 2^h` converges (it adds up to 2). Most nodes sit near the
  bottom of the tree and barely move, so even though there are `n / 2`
  of them, their contribution is only O(n).
- **The extraction phase is O(n log n):** `n - 1` extractions, each
  one root-to-leaf sift-down of cost O(log n).

Best, average, and worst case are all O(n log n), because no input can
change the tree's shape or the number of extractions. The overheads
heap sort pays instead: every element is swapped on the order of
`log n` times over the whole run, and the strided index arithmetic
(`2i + 1`, `2i + 2`) accesses memory less locally than a linear scan.
Heap sort is also not stable, because the heap swaps elements freely.

### Against merge sort and quick sort

`sorts.py` contains the merge sort from the Assignment 2 repository
and the randomized quick sort from the Assignment 3 repository, so I
am comparing against the same quick sort whose deterministic variant
blew up on ordered input in Assignment 3. Measured wall times (ms);
the full data is in `results/benchmark_results.csv`:

| Dataset        | n     | heap_sort | merge_sort | quick_sort |
| -------------- | ----- | --------: | ---------: | ---------: |
| random         | 1,024 |       0.70 |       1.81 |       0.47 |
| random         | 8,192 |       8.72 |      15.30 |       6.23 |
| random         | 32,768|      43.84 |      67.06 |      32.03 |
| sorted         | 1,024 |       0.74 |       1.44 |       0.42 |
| sorted         | 8,192 |       9.06 |      12.55 |       6.40 |
| sorted         | 32,768|      44.02 |      55.36 |      29.89 |
| reverse_sorted | 1,024 |       0.61 |       1.46 |       0.43 |
| reverse_sorted | 8,192 |       7.86 |      12.93 |       5.91 |
| reverse_sorted | 32,768|      37.70 |      53.80 |      25.96 |

Findings:

- **No input-dependent worst case.** All three algorithms grow about
  2.1–2.4x per doubling on every dataset — the n log n signature —
  including on sorted and reverse-sorted input. That is the contrast
  with Assignment 3: the deterministic quick sort there needed a size
  cap on ordered data, while here every dataset runs to 32,768.
  Randomized quick sort keeps the n log n curve on ordered input
  because its random pivot destroys the dependence on input order;
  heap sort and merge sort never had the dependence to begin with.
- **Constant factors.** On random data the ranking is
  quick_sort < heap_sort < merge_sort (at n = 32,768: 32.0 vs 43.8 vs
  67.1 ms). Heap sort's O(1) space matches quick sort's, but its
  repeated root-to-leaf sifting with strided index access costs more
  per element than quick sort's linear partition scans, and merge
  sort's extra list allocations make it the slowest in wall time.
  The memory column shows the same trade from the other side: merge
  sort peaks at 0.63 MB at n = 32,768 (its O(n) auxiliary space)
  while heap sort and quick sort stay near zero.
- **The practical takeaway** matches the theory: when a *guaranteed*
  n log n is required (adversarial or real-time input where quick
  sort's rare quadratic runs are unacceptable) and the extra space
  must be O(1), heap sort is the right choice — you pay a constant
  factor for the guarantee.

### Complexity summary

- **Heap sort:** O(n log n) time in all cases, O(1) extra space, in
  place, not stable.
- **Merge sort:** O(n log n) time in all cases, O(n) extra space,
  stable.
- **Randomized quick sort:** O(n log n) expected time on every input,
  O(log n) expected stack space, in place, not stable.

## Priority queue and scheduler

### Design choices

I stored the heap as a plain Python list with the structure held
implicitly by the index formulas (parent `(i - 1) // 2`, children
`2i + 1` and `2i + 2`). A list beats a pointer-based tree for this
purpose: parent/child lookups are constant-time arithmetic, the memory
is contiguous, and no node objects or links are needed.

I used a **max-heap with higher priority meaning more urgent**. The
scheduler's dispatch rule wants the most urgent ready task first, so
a max-heap is the natural fit (a min-heap would work with the
comparisons flipped). Ties go to the task that arrived earlier, which
keeps the rule deterministic.

Each `Task` stores `task_id`, `priority`, `arrival`, `deadline`, and
`run_time` — enough to both schedule and check deadlines. Each task
also stores its current position in the heap list, updated on every
swap; that is what lets `increase_key` / `decrease_key` start from the
task's own slot instead of scanning for it.

### Operation costs

| Operation                  | Cost      | Why                                          |
| -------------------------- | --------- | -------------------------------------------- |
| `insert(task)`             | O(log n)  | append, then one sift-up along the edge      |
| `extract_max()`            | O(log n)  | move last element to root, sift down         |
| `increase_key(task, new)`  | O(log n)  | set key, sift up from the task's slot        |
| `decrease_key(task, new)`  | O(log n)  | set key, sift down from the task's slot      |
| `peek()`                   | O(1)      | the maximum is always at index 0             |
| `is_empty()`               | O(1)      | a length check                               |

Each heap operation is one sift up or down along a root-to-leaf path
of length O(log n), and the two O(1) operations are a length check and
a read of the root.

### The scheduling simulation

`scheduler.py` runs a **non-preemptive priority scheduler**: when the
processor is free it dispatches the ready task with the highest
priority (ties: earlier arrival), and a dispatched task runs to
completion. Tasks join the ready queue at their arrival time; if
nothing is ready the clock jumps to the next arrival.

The sample workload is small enough to check by hand, and `tests.py`
pins the exact numbers:

| task     | prio | arr | run | finish | wait | turn | deadline |
| -------- | ----: | ---: | ---: | -----: | ---: | ---: | -------: |
| incident |     5 |    0 |    2 |      2 |    0 |    2 |        3 |
| build    |     3 |    0 |    2 |      4 |    2 |    4 |        6 |
| report   |     2 |    2 |    1 |      5 |    2 |    3 |        8 |
| backup   |     1 |    0 |    3 |      8 |    5 |    8 |       10 |

Averages: finish 4.75, wait 2.25, turnaround 4.25; 0 deadline misses.
The dispatch order matches the hand computation: the incident runs
0–2, the build 2–4, the report (arrived at 2) 4–5, the backup 5–8.

I also ran a random workload (100 tasks, priorities 1–10, arrivals
0–50, run times 1–5, deadlines 1–80, seed 42):

- Averages: finish 144.93, wait 116.69, turnaround 119.56.
- **88 of 100 tasks miss their deadlines.** The workload needs about
  287 time units of processing, while most deadlines fall between 1
  and 80 — the deadlines are simply infeasible under this load.
- The wait times show the dispatch rule working: high-priority tasks
  barely wait (several with wait 0–1), while the lowest-priority
  tasks wait 240+ units. Two things worth noting: (1) priority
  scheduling optimizes *priority order*, not deadlines — misses happen
  at every priority level once the queue backs up, so a
  deadline-driven policy (earliest-deadline-first) would be the right
  tool for this workload; (2) the long waits at the bottom of the
  priority range are the classic starvation risk of priority
  scheduling, which aging (raising a task's priority the longer it
  waits) is the standard mitigation.

## Benchmark notes

- All datasets run from 1,024 to 32,768 elements; unlike Assignment 3,
  no dataset needed a size cap because none of the three algorithms
  has an input-dependent worst case.
- Time is wall time around the sort call, averaged over 3 runs (1 run
  for sizes >= 16,384); memory is the peak of Python allocations
  tracked by `tracemalloc`.
- `sorts.py` is a verbatim copy of the merge sort from the
  Assignment 2 repository and the randomized quick sort from the
  Assignment 3 repository, so this repository is self-contained.

## References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022).
  *Introduction to Algorithms* (4th ed.). MIT Press.
