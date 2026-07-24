import time
from typing import TypedDict

class TaskVector(TypedDict):
    id: str
    target: str
    priority: int
    data_payload: dict
    timestamp: float

class BeeScoutEngine:
    """
    Bee Architecture: Global Exploration and Task Swapping.
    Scout Bees map problem boundaries and broadcast Task Vectors (Waggle Dance).
    Worker agents dynamically swap castes based on queue pressure.
    """

    def __init__(self):
        # Global Waggle Dance Task Queue
        self.task_queue: list[TaskVector] = []

    def perform_waggle_dance(self, target: str, priority: int, data_payload: dict = None) -> TaskVector:
        """Scout Bee broadcasts a discovered resource/task vector to the hive."""
        task_id = f"vec_{int(time.time()*1000)}"
        task_vec: TaskVector = {
            "id": task_id,
            "target": target,
            "priority": priority,
            "data_payload": data_payload or {},
            "timestamp": time.time()
        }
        self.task_queue.append(task_vec)
        # Sort queue by priority (higher priority first)
        self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
        print(f"[Bee Waggle Dance] Broadcasted Task Vector '{target}' (Priority: {priority}, Queue Size: {len(self.task_queue)})")
        return task_vec

    def determine_worker_caste(self) -> str:
        """
        Dynamic Caste Swapping:
        Determines whether general workers should act as 'Scout', 'Forager', or 'DataProcessor'
        based on task queue pressure.
        """
        queue_len = len(self.task_queue)
        if queue_len == 0:
            return "Scout"  # No pending tasks -> fan out and explore
        elif queue_len > 5:
            return "DataProcessor"  # Heavy queue -> workers become data processors
        else:
            return "Forager"  # Moderate queue -> gather data

    def consume_next_task(self) -> TaskVector:
        """Pulls the highest priority task vector from the Waggle Dance queue."""
        if not self.task_queue:
            return None
        return self.task_queue.pop(0)

bee_scout = BeeScoutEngine()
