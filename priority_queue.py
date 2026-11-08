"""
MSCS 532 - Assignment 4
Priority queue on a binary max-heap (Part 2).

By: Alfredo Rosado
Date: 11-02-26

The queue is stored in a plain Python list, with the heap property
maintained implicitly: the parent of index i is (i - 1) // 2 and its
children are 2i + 1 and 2i + 2. A list is a good fit because the
index arithmetic is constant time, the memory is contiguous (good
cache behavior), and no pointer objects are needed - the same reason
the heap in main.py is array-based.

Higher priority values mean more urgent, so the queue is a MAX-heap:
extract_max returns the most urgent task first. A min-heap would
work just as well with the comparisons flipped; the max-heap choice
follows the scheduler's dispatch rule, which wants the highest
priority value first.

Each Task remembers its current position in the heap list, so a key
change (increase_key / decrease_key) can start from the task's own
spot instead of searching for it.

Based on Chapter 6 of Cormen, Leiserson, Rivest & Stein,
"Introduction to Algorithms" (4th ed., 2022).
"""


class Task:
    """A unit of work for the scheduler.

    Parameter: task_id  - a unique identifier
               priority - urgency; HIGHER means more urgent
               arrival  - time the task becomes ready
               deadline - time the task should be done by (or None)
               run_time - how long the task needs the processor
    """

    def __init__(self, task_id, priority, arrival=0, deadline=None,
                 run_time=1):
        self.task_id = task_id
        self.priority = priority
        self.arrival = arrival
        self.deadline = deadline
        self.run_time = run_time
        # Where this task sits in the heap list; -1 means the task is
        # not currently in a heap.
        self._heap_index = -1

    def __repr__(self):
        return (f"Task(id={self.task_id!r}, priority={self.priority}, "
                f"arrival={self.arrival}, run_time={self.run_time})")


class PriorityQueue:
    """Max-heap priority queue of Task objects.

    Higher priority extracts first; on equal priority the task that
    arrived earlier extracts first.
    """

    def __init__(self):
        self._heap = []

    def _greater(self, a, b):
        """True if task a should sit closer to the root than b:
        higher priority first, earlier arrival on ties."""
        if a.priority != b.priority:
            return a.priority > b.priority
        return a.arrival < b.arrival

    def _swap(self, i, j):
        """Exchange the tasks at i and j, keeping each task's recorded
        heap position accurate."""
        a, b = self._heap[i], self._heap[j]
        self._heap[i], self._heap[j] = b, a
        a._heap_index = j
        b._heap_index = i

    def _sift_up(self, i):
        """Move the task at i up until it is no larger than its parent."""
        while i > 0:
            parent = (i - 1) // 2
            if not self._greater(self._heap[i], self._heap[parent]):
                return
            self._swap(i, parent)
            i = parent

    def _sift_down(self, i):
        """Move the task at i down until the heap property holds."""
        n = len(self._heap)
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            largest = i
            if left < n and self._greater(self._heap[left], self._heap[largest]):
                largest = left
            if right < n and self._greater(self._heap[right], self._heap[largest]):
                largest = right
            if largest == i:
                return
            self._swap(i, largest)
            i = largest

    def insert(self, task):
        """Add task to the queue.

        Parameter: task - a Task to enqueue
        Return:    None

        Complexity: O(log n) - one append, then sift up along the
        left edge of the heap.
        """
        task._heap_index = len(self._heap)
        self._heap.append(task)
        self._sift_up(task._heap_index)

    def extract_max(self):
        """Remove and return the highest-priority task.

        Return:    the most urgent task currently in the queue
        Raises:   IndexError if the queue is empty

        Complexity: O(log n) - move the last task to the root, then
        sift it down.
        """
        if not self._heap:
            raise IndexError("extract_max on an empty priority queue")
        top = self._heap[0]
        last = self._heap.pop()
        if self._heap:
            self._heap[0] = last
            last._heap_index = 0
            self._sift_down(0)
        top._heap_index = -1
        return top

    def increase_key(self, task, new_priority):
        """Raise task's priority to new_priority.

        Parameter: task          - a Task currently in the queue
                   new_priority  - the (higher) priority to set
        Raises:   KeyError  if the task is not in the queue
                  ValueError if new_priority is not higher

        Complexity: O(log n) - the task's position is stored on the
        task itself, then it is sifted up from there.
        """
        if task._heap_index < 0:
            raise KeyError("task is not in the queue")
        if new_priority < task.priority:
            raise ValueError("increase_key must not lower the priority")
        task.priority = new_priority
        self._sift_up(task._heap_index)

    def decrease_key(self, task, new_priority):
        """Lower task's priority to new_priority.

        Parameter: task          - a Task currently in the queue
                   new_priority  - the (lower) priority to set
        Raises:   KeyError  if the task is not in the queue
                  ValueError if new_priority is not lower

        Complexity: O(log n) - change the key, then sift down from
        the task's recorded position.
        """
        if task._heap_index < 0:
            raise KeyError("task is not in the queue")
        if new_priority > task.priority:
            raise ValueError("decrease_key must not raise the priority")
        task.priority = new_priority
        self._sift_down(task._heap_index)

    def peek(self):
        """Return the highest-priority task without removing it.

        Complexity: O(1).
        """
        if not self._heap:
            raise IndexError("peek on an empty priority queue")
        return self._heap[0]

    def is_empty(self):
        """True if no tasks are queued.

        Complexity: O(1).
        """
        return not self._heap

    def __len__(self):
        return len(self._heap)


def main():
    # A small demo: three tasks, then a priority change
    backup = Task("backup", priority=1, arrival=0, run_time=5)
    email = Task("email", priority=3, arrival=0, run_time=2)
    incident = Task("incident", priority=5, arrival=0, run_time=1)

    pq = PriorityQueue()
    for t in (backup, email, incident):
        pq.insert(t)

    # The incident gets escalated, and the backup is demoted
    pq.increase_key(incident, 8)
    pq.decrease_key(backup, 0)

    while not pq.is_empty():
        print(pq.extract_max())


if __name__ == "__main__":
    main()
