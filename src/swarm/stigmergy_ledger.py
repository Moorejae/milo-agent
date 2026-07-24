import time
import math
import threading
from src.hive_queen_schema import hive_vault

class StigmergyLedger:
    """
    Ant Architecture: Decentralized Pathing and Stigmergy.
    Tracks digital pheromone weights for tool/API paths with exponential decay.
    Prevents the swarm from getting stuck in outdated routines.
    """

    def __init__(self, decay_rate: float = 0.05):
        # Ledger storing: {path_name: {"weight": float, "last_updated": float}}
        self.pheromones: dict[str, dict] = {}
        self.decay_rate = decay_rate
        self.vault = hive_vault

    def deposit_pheromone(self, path_name: str, initial_weight: float = 1.0):
        """Deposits or reinforces a pheromone trail for a successful execution path."""
        now = time.time()
        current = self.get_path_weight(path_name)
        new_weight = current + initial_weight
        self.pheromones[path_name] = {
            "weight": new_weight,
            "last_updated": now
        }
        print(f"[Ant Stigmergy] Deposited pheromone on '{path_name}' -> New Weight: {new_weight:.2f}")
        self._bg_sync()

    def get_path_weight(self, path_name: str) -> float:
        """Returns the current decayed weight for a path using W(t) = W0 * e^(-lambda * dt)."""
        if path_name not in self.pheromones:
            return 0.0
        
        data = self.pheromones[path_name]
        dt = (time.time() - data["last_updated"]) / 3600.0  # Elapsed hours
        decayed_weight = data["weight"] * math.exp(-self.decay_rate * dt)
        
        # Evaporate completely if weight drops below threshold
        if decayed_weight < 0.01:
            decayed_weight = 0.0

        return round(decayed_weight, 4)

    def get_optimal_path(self, available_paths: list[str]) -> str:
        """Selects the path with the highest pheromone weight, or defaults to the first path if none."""
        if not available_paths:
            return ""
        
        best_path = available_paths[0]
        max_weight = -1.0

        for path in available_paths:
            w = self.get_path_weight(path)
            if w > max_weight:
                max_weight = w
                best_path = path

        print(f"[Ant Stigmergy] Optimal path selected: '{best_path}' (Weight: {max_weight:.2f})")
        return best_path

    def _bg_sync(self):
        """Asynchronously logs active pheromone trails to Obsidian Vault."""
        def _bg_write():
            summary = "\n".join([f"- **{k}**: {v['weight']:.2f} (Updated: {time.ctime(v['last_updated'])})" for k, v in self.pheromones.items()])
            file_content = f"# Digital Pheromone Ledger (Ant Stigmergy)\n\n{summary}"
            self.vault.write_file_async("brain/pheromones.md", file_content, commit_msg="Update Pheromone Ledger")
        threading.Thread(target=_bg_write, daemon=True).start()

stigmergy_ledger = StigmergyLedger()
