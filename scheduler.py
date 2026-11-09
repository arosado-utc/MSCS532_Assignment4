"""
MSCS 532 - Assignment 4
Task-scheduling simulation (Part 2, applications).

Runs a non-preemptive priority scheduler: when the processor is free,
the ready task with the highest priority runs to completion. Tasks
become ready at their arrival time. The simulation records the
finish, wait, and turnaround time of every task.

Run:  python3 scheduler.py
"""

import random

from priority_queue import PriorityQueue, Task


def run_scheduler(tasks):
    """Schedule tasks with a non-preemptive priority rule.

    Parameter: tasks - a list of Task objects (each with arrival and
                       run_time fields)
    Return:    a dict with per-task results and summary statistics:
               {
                 "results":        {task_id: (finish, wait, turnaround)},
                 "avg_finish":     mean finish time,
                 "avg_wait":       mean waiting time,
                 "avg_turnaround": mean turnaround time,
                 "deadline_misses": tasks finishing after their deadline,
               }
    """
    ready = PriorityQueue()
    results = {}
    time = 0
    waiting = sorted(tasks, key=lambda t: t.arrival)
    next_idx = 0

    while next_idx < len(waiting) or not ready.is_empty():
        # Every task whose arrival time has come joins the ready queue.
        while (next_idx < len(waiting)
               and waiting[next_idx].arrival <= time):
            ready.insert(waiting[next_idx])
            next_idx += 1

        if ready.is_empty():
            # Nothing ready yet: jump to the next arrival.
            time = waiting[next_idx].arrival
            continue

        task = ready.extract_max()
        start = time
        time += task.run_time
        results[task.task_id] = (
            time,                      # finish
            start - task.arrival,      # wait
            time - task.arrival,       # turnaround
        )

    n = len(results)
    deadline_misses = sum(
        1 for t in tasks
        if t.deadline is not None and results[t.task_id][0] > t.deadline
    )
    return {
        "results": results,
        "avg_finish": sum(r[0] for r in results.values()) / n,
        "avg_wait": sum(r[1] for r in results.values()) / n,
        "avg_turnaround": sum(r[2] for r in results.values()) / n,
        "deadline_misses": deadline_misses,
    }


def sample_workload():
    """A small fixed workload, designed so the dispatch order is easy
    to follow by hand.

    At t=0 all three tasks are ready; the incident (priority 5) runs
    first, then the build (priority 3), then the backup (priority 1).
    The report task arrives at t=2 while the incident is running.
    """
    return [
        Task("backup", priority=1, arrival=0, deadline=10, run_time=3),
        Task("build", priority=3, arrival=0, deadline=6, run_time=2),
        Task("incident", priority=5, arrival=0, deadline=3, run_time=2),
        Task("report", priority=2, arrival=2, deadline=8, run_time=1),
    ]


def random_workload(seed=42, n=100):
    """A larger reproducible workload: n tasks with random priorities,
    arrivals, run times, and deadlines."""
    rng = random.Random(seed)
    return [
        Task(f"t{i:03d}",
             priority=rng.randint(1, 10),
             arrival=rng.randint(0, 50),
             deadline=rng.randint(1, 80),
             run_time=rng.randint(1, 5))
        for i in range(n)
    ]


def print_report(tasks, report):
    """Print a per-task table and the summary statistics."""
    order = sorted(tasks, key=lambda t: report["results"][t.task_id][0])
    print(f"{'task':10s} {'prio':>4s} {'arr':>4s} {'run':>4s} "
          f"{'fin':>4s} {'wait':>5s} {'turn':>5s} {'deadline':>8s}")
    for t in order:
        finish, wait, turn = report["results"][t.task_id]
        dl = f"{t.deadline}" if t.deadline is not None else "-"
        print(f"{t.task_id:10s} {t.priority:4d} {t.arrival:4d} "
              f"{t.run_time:4d} {finish:4d} {wait:5d} {turn:5d} {dl:>8s}")
    print()
    print(f"avg finish:     {report['avg_finish']:.2f}")
    print(f"avg wait:       {report['avg_wait']:.2f}")
    print(f"avg turnaround: {report['avg_turnaround']:.2f}")
    print(f"deadline misses: {report['deadline_misses']} of {len(tasks)}")


def main():
    print("Sample workload (hand-checkable):")
    tasks = sample_workload()
    print_report(tasks, run_scheduler(tasks))
    print()

    print("Random workload (100 tasks, seed 42):")
    tasks = random_workload()
    print_report(tasks, run_scheduler(tasks))


if __name__ == "__main__":
    main()
