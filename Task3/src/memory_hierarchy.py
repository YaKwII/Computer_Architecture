import logging
from collections import deque, OrderedDict
from enum import Enum
from typing import Optional
import random

# Configure logging — change level to logging.DEBUG for more detail
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)


class ReplacementPolicy(Enum):
    FIFO   = "FIFO"
    LRU    = "LRU"
    RANDOM = "RANDOM"


class MemoryLevelName(Enum):
    SSD  = "SSD"
    DRAM = "DRAM"
    L3   = "L3"
    L2   = "L2"
    L1   = "L1"


class MemoryLevel:
    """
    Represents one level in the memory hierarchy.
    Supports FIFO, LRU, and RANDOM cache replacement policies.
    Uses a set for O(1) membership checks alongside a deque/OrderedDict for ordering.
    """

    def __init__(
        self,
        name: str,
        capacity: int,
        policy: ReplacementPolicy = ReplacementPolicy.FIFO
    ) -> None:
        if capacity <= 0:
            raise ValueError(f"{name} capacity must be a positive integer, got {capacity}")

        self.name     = name
        self.capacity = capacity
        self.policy   = policy
        self.hits     = 0
        self.misses   = 0

        # Internal storage — OrderedDict used for LRU; deque used for FIFO/RANDOM
        if policy == ReplacementPolicy.LRU:
            self._lru: OrderedDict = OrderedDict()
        else:
            self._fifo: deque = deque()

        self._index: set = set()  # O(1) membership check for all policies

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def contains(self, item: str) -> bool:
        """Return True if item is in this memory level."""
        return item in self._index

    def store(self, item: str) -> None:
        """Store item. If already present count as a hit; otherwise evict if full, then insert."""
        if item in self._index:
            self.hits += 1
            if self.policy == ReplacementPolicy.LRU:
                self._lru.move_to_end(item)  # Mark as recently used
            return

        self.misses += 1
        if self._size() >= self.capacity:
            self._evict()

        self._insert(item)
        logging.info("  [%s] STORE: %s", self.name, item)

    def remove(self, item: str) -> None:
        """Remove item explicitly (used during write-back or manual eviction)."""
        if item not in self._index:
            raise ValueError(f"Item '{item}' not found in {self.name} during remove operation.")
        self._delete(item)

    def is_full(self) -> bool:
        """Return True if this level has reached capacity."""
        return self._size() >= self.capacity

    def contents(self) -> list:
        """Return current contents as a list (oldest first for FIFO; MRU order for LRU)."""
        if self.policy == ReplacementPolicy.LRU:
            return list(self._lru.keys())
        return list(self._fifo)

    def stats(self) -> dict:
        """Return hit/miss statistics for this level."""
        total = self.hits + self.misses
        ratio = self.hits / total if total > 0 else 0.0
        return {
            "name":      self.name,
            "hits":      self.hits,
            "misses":    self.misses,
            "hit_ratio": ratio,
            "contents":  self.contents(),
        }

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _size(self) -> int:
        return len(self._index)

    def _insert(self, item: str) -> None:
        self._index.add(item)
        if self.policy == ReplacementPolicy.LRU:
            self._lru[item] = True
        else:
            self._fifo.append(item)

    def _delete(self, item: str) -> None:
        self._index.discard(item)
        if self.policy == ReplacementPolicy.LRU:
            self._lru.pop(item, None)
        elif item in self._fifo:
            self._fifo.remove(item)

    def _evict(self) -> None:
        """Evict one item based on the replacement policy."""
        if self.policy == ReplacementPolicy.FIFO:
            evicted = self._fifo.popleft()
            self._index.discard(evicted)
        elif self.policy == ReplacementPolicy.LRU:
            evicted, _ = self._lru.popitem(last=False)  # Least recently used
            self._index.discard(evicted)
        elif self.policy == ReplacementPolicy.RANDOM:
            evicted = random.choice(list(self._index))
            self._delete(evicted)
        logging.info("  [%s] EVICT (%s): %s", self.name, self.policy.value, evicted)

    def __repr__(self) -> str:
        return f"{self.name}(capacity={self.capacity}, items={self.contents()})"


# --------------------------------------------------------------------------- #

class MemoryHierarchy:
    """
    Manages the full SSD -> DRAM -> L3 -> L2 -> L1 -> CPU hierarchy.
    Enforces no-bypass rule: data must travel one level at a time.
    """

    def __init__(
        self,
        ssd_size:  int,
        dram_size: int,
        l3_size:   int,
        l2_size:   int,
        l1_size:   int,
        policy: ReplacementPolicy = ReplacementPolicy.FIFO
    ) -> None:
        sizes = [ssd_size, dram_size, l3_size, l2_size, l1_size]
        names = ["SSD", "DRAM", "L3", "L2", "L1"]

        # Validate each size is positive
        for name, size in zip(names, sizes):
            if size <= 0:
                raise ValueError(f"{name} size must be a positive integer, got {size}")

        # Enforce hierarchy: SSD > DRAM > L3 > L2 > L1
        for i in range(len(sizes) - 1):
            if sizes[i] <= sizes[i + 1]:
                raise ValueError(
                    f"Hierarchy violated: {names[i]} ({sizes[i]}) must be "
                    f"larger than {names[i+1]} ({sizes[i+1]})"
                )

        self.ssd  = MemoryLevel(MemoryLevelName.SSD.value,  ssd_size,  ReplacementPolicy.FIFO)  # SSD always FIFO
        self.dram = MemoryLevel(MemoryLevelName.DRAM.value, dram_size, ReplacementPolicy.FIFO)  # DRAM always FIFO
        self.l3   = MemoryLevel(MemoryLevelName.L3.value,   l3_size,   policy)
        self.l2   = MemoryLevel(MemoryLevelName.L2.value,   l2_size,   policy)
        self.l1   = MemoryLevel(MemoryLevelName.L1.value,   l1_size,   policy)

        self.levels: list[MemoryLevel] = [self.ssd, self.dram, self.l3, self.l2, self.l1]
        self.clock:  int  = 0
        self.policy: ReplacementPolicy = policy

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def load_to_ssd(self, item: str) -> None:
        """Pre-load an instruction into SSD (startup only, bypasses normal rules)."""
        self.ssd._index.add(item)
        self.ssd._fifo.append(item)

    def access(self, item: str) -> None:
        """
        CPU requests an instruction.
        Data moves up one level at a time from wherever it currently resides.
        CPU reads exclusively from L1.
        """
        self._tick()
        logging.info("  ACCESS REQUEST: %s", item)

        found_at = self._find(item)
        if found_at is None:
            logging.warning("  ERROR: %s not found anywhere in hierarchy!", item)
            return

        start_idx = self.levels.index(found_at)

        # Move item upward one step at a time until it reaches L1
        for i in range(start_idx, len(self.levels) - 1):
            self._move_item(src=self.levels[i], dest=self.levels[i + 1], item=item)

        logging.info("  CPU FETCH: %s from L1 ✓", item)

    def write_back(self, item: str) -> None:
        """
        Write data from L1 back down through the hierarchy.
        Data moves one level at a time.
        """
        self._tick()
        logging.info("  WRITE-BACK: %s", item)
        for i in range(len(self.levels) - 1, 0, -1):
            src  = self.levels[i]
            dest = self.levels[i - 1]
            if src.contains(item):
                logging.info("  WRITE: %s  %s -> %s", item, src.name, dest.name)
                dest.store(item)

    def print_config(self) -> None:
        """Print the memory hierarchy configuration."""
        print("\n=== Memory Hierarchy Configuration ===")
        print(f"  Cache Replacement Policy : {self.policy.value}")
        for level in self.levels:
            print(f"  {level.name:5s} capacity : {level.capacity:4d} instructions")
        print()

    def print_state(self) -> None:
        """Print the final state of every memory level."""
        print(f"\n=== Final State (Clock: {self.clock} cycles) ===")
        for level in self.levels:
            s = level.stats()
            print(
                f"  {s['name']:5s} | "
                f"hits: {s['hits']:3d} | "
                f"misses: {s['misses']:3d} | "
                f"hit ratio: {s['hit_ratio']:.0%} | "
                f"contents: {s['contents']}"
            )

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _tick(self) -> None:
        """Advance the simulation clock by one cycle."""
        self.clock += 1
        logging.info("\n[Clock Cycle %d]", self.clock)

    def _find(self, item: str) -> Optional[MemoryLevel]:
        """Search from L1 down to SSD to find the closest level that holds item."""
        for level in reversed(self.levels):
            if level.contains(item):
                return level
        return None

    def _move_item(self, src: MemoryLevel, dest: MemoryLevel, item: str) -> None:
        """Move item from src to dest if dest does not already have it."""
        if not dest.contains(item):
            logging.info("  MOVE: %s  %s -> %s", item, src.name, dest.name)
            dest.store(item)
            # Note: item is intentionally kept in lower levels (no removal on read)
            # It will only be removed when evicted due to capacity limits
