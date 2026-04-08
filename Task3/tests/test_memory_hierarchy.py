import pytest
from src.memory_hierarchy import MemoryLevel, MemoryHierarchy, ReplacementPolicy


# ─────────────────────────── MemoryLevel tests ───────────────────────────── #

class TestMemoryLevel:

    def test_store_and_contains(self):
        level = MemoryLevel("L1", 4)
        level.store("INSTR_01")
        assert level.contains("INSTR_01")
        assert not level.contains("INSTR_99")

    def test_hit_counted_on_duplicate_store(self):
        level = MemoryLevel("L1", 4)
        level.store("INSTR_01")
        level.store("INSTR_01")  # second store = hit
        assert level.hits == 1
        assert level.misses == 1

    def test_fifo_eviction(self):
        level = MemoryLevel("L1", 2, ReplacementPolicy.FIFO)
        level.store("A")
        level.store("B")
        level.store("C")  # A should be evicted (oldest)
        assert not level.contains("A")
        assert level.contains("B")
        assert level.contains("C")

    def test_lru_eviction(self):
        level = MemoryLevel("L1", 2, ReplacementPolicy.LRU)
        level.store("A")
        level.store("B")
        level.store("A")  # Access A again — B is now least recently used
        level.store("C")  # B should be evicted
        assert not level.contains("B")
        assert level.contains("A")
        assert level.contains("C")

    def test_random_eviction_removes_one(self):
        level = MemoryLevel("L1", 2, ReplacementPolicy.RANDOM)
        level.store("A")
        level.store("B")
        level.store("C")  # One of A/B should be evicted
        assert len(level.contents()) == 2
        assert level.contains("C")

    def test_remove_existing_item(self):
        level = MemoryLevel("L1", 4)
        level.store("INSTR_01")
        level.remove("INSTR_01")
        assert not level.contains("INSTR_01")

    def test_remove_nonexistent_raises(self):
        level = MemoryLevel("L1", 4)
        with pytest.raises(ValueError, match="not found"):
            level.remove("GHOST")

    def test_invalid_capacity_raises(self):
        with pytest.raises(ValueError, match="positive integer"):
            MemoryLevel("L1", 0)

    def test_hit_ratio_stats(self):
        level = MemoryLevel("L1", 4)
        level.store("A")
        level.store("A")  # hit
        s = level.stats()
        assert s["hit_ratio"] == 0.5


# ────────────────────────── MemoryHierarchy tests ────────────────────────── #

class TestMemoryHierarchy:

    def _make_sim(self, policy=ReplacementPolicy.FIFO):
        sim = MemoryHierarchy(64, 32, 16, 8, 4, policy=policy)
        for i in range(1, 10):
            sim.load_to_ssd(f"INSTR_{i:02d}")
        return sim

    def test_hierarchy_size_validation(self):
        with pytest.raises(ValueError, match="Hierarchy violated"):
            MemoryHierarchy(4, 32, 16, 8, 2)  # SSD < DRAM — invalid

    def test_access_moves_data_to_l1(self):
        sim = self._make_sim()
        sim.access("INSTR_01")
        assert sim.l1.contains("INSTR_01")
        assert sim.l2.contains("INSTR_01")
        assert sim.l3.contains("INSTR_01")
        assert sim.dram.contains("INSTR_01")

    def test_second_access_is_l1_hit(self):
        sim = self._make_sim()
        sim.access("INSTR_01")
        hits_before = sim.l1.hits
        sim.access("INSTR_01")
        assert sim.l1.hits > hits_before

    def test_clock_advances_per_access(self):
        sim = self._make_sim()
        sim.access("INSTR_01")
        sim.access("INSTR_02")
        assert sim.clock == 2

    def test_access_unknown_item(self):
        sim = self._make_sim()
        # Should not raise — logs a warning and returns
        sim.access("INSTR_99")

    def test_lru_policy_propagates(self):
        sim = self._make_sim(policy=ReplacementPolicy.LRU)
        assert sim.l1.policy == ReplacementPolicy.LRU
        assert sim.l2.policy == ReplacementPolicy.LRU
        assert sim.l3.policy == ReplacementPolicy.LRU
