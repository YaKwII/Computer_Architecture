from collections import deque

class MemoryLevel:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.data = deque()  # FIFO eviction
        self.hits = 0
        self.misses = 0

    def contains(self, item):
        return item in self.data

    def store(self, item):
        if item in self.data:
            self.hits += 1
            return
        self.misses += 1
        if len(self.data) >= self.capacity:
            evicted = self.data.popleft()
            print(f"  [{self.name}] EVICT: {evicted}")
        self.data.append(item)
        print(f"  [{self.name}] STORE: {item}")

    def remove(self, item):
        if item in self.data:
            self.data.remove(item)

    def is_full(self):
        return len(self.data) >= self.capacity

    def __repr__(self):
        return f"{self.name}({list(self.data)})"


class MemoryHierarchy:
    def __init__(self, ssd_size, dram_size, l3_size, l2_size, l1_size):
        sizes = [ssd_size, dram_size, l3_size, l2_size, l1_size]
        names = ["SSD", "DRAM", "L3", "L2", "L1"]
        for i in range(len(sizes) - 1):
            if sizes[i] <= sizes[i+1]:
                raise ValueError(f"{names[i]} must be larger than {names[i+1]}")

        self.ssd  = MemoryLevel("SSD",  ssd_size)
        self.dram = MemoryLevel("DRAM", dram_size)
        self.l3   = MemoryLevel("L3",   l3_size)
        self.l2   = MemoryLevel("L2",   l2_size)
        self.l1   = MemoryLevel("L1",   l1_size)

        self.levels = [self.ssd, self.dram, self.l3, self.l2, self.l1]
        self.clock  = 0

    def load_to_ssd(self, item):
        """Load an instruction directly into SSD at startup."""
        self.ssd.data.append(item)

    def tick(self):
        """Advance the clock by one cycle."""
        self.clock += 1
        print(f"\n[Clock Cycle {self.clock}]")

    def access(self, item):
        """
        Fetch an instruction.
        Moves data step by step: SSD -> DRAM -> L3 -> L2 -> L1.
        CPU reads from L1 only.
        """
        self.tick()
        print(f"  ACCESS REQUEST: {item}")

        found_at = None
        for level in reversed(self.levels):
            if level.contains(item):
                found_at = level
                break

        if found_at is None:
            print(f"  ERROR: {item} not found anywhere in hierarchy!")
            return

        levels = self.levels
        start_idx = levels.index(found_at)

        for i in range(start_idx, len(levels) - 1):
            src  = levels[i]
            dest = levels[i + 1]
            if not dest.contains(item):
                print(f"  MOVE: {item}  {src.name} -> {dest.name}")
                dest.store(item)

        print(f"  CPU FETCH: {item} from L1 ✓")

    def write_back(self, item):
        """Write an item back from L1 down through the hierarchy."""
        self.tick()
        print(f"  WRITE-BACK: {item}")
        for i in range(len(self.levels) - 1, 0, -1):
            src  = self.levels[i]
            dest = self.levels[i - 1]
            if src.contains(item):
                print(f"  WRITE: {item}  {src.name} -> {dest.name}")
                dest.store(item)

    def print_config(self):
        print("Memory Hierarchy Configuration:")
        print(f"  SSD  capacity : {self.ssd.capacity}  instructions")
        print(f"  DRAM capacity : {self.dram.capacity} instructions")
        print(f"  L3   capacity : {self.l3.capacity}  instructions")
        print(f"  L2   capacity : {self.l2.capacity}   instructions")
        print(f"  L1   capacity : {self.l1.capacity}   instructions")

    def print_state(self):
        print(f"\nTotal Clock Cycles: {self.clock}")
        for level in self.levels:
            print(f"  {level.name:5s} | hits: {level.hits} | misses: {level.misses} | contents: {list(level.data)}")
