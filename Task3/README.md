# Processor Design Task 3 — Memory Hierarchy Simulation

**Georgia State University — CSC 4210/6210 Computer Architecture — Spring 2026**

---

## Overview

Simulates an SSD → DRAM → L3 → L2 → L1 → CPU memory hierarchy.
Data moves **one level at a time** — no bypassing allowed.
All data is treated as **32-bit instructions**.

---

## Features

- Clock-driven simulation (each access = one clock cycle)
- Configurable sizes for every memory level
- Enforces hierarchy rule: `SSD > DRAM > L3 > L2 > L1`
- Read (fetch) and write-back operations
- Three cache replacement policies: **FIFO**, **LRU**, **RANDOM** (bonus)
- O(1) cache membership checks via internal set index
- Hit / miss tracking with hit ratio per level
- Full instruction access trace printed per clock cycle
- Final state of every memory level printed at end
- Command-line interface (CLI) for custom configurations
- Unit tests with `pytest`

---

## How to Run

### Default run (FIFO, default sizes)
```bash
cd Task3
python src/main.py
```

### Custom sizes and policy via CLI
```bash
python src/main.py --ssd 128 --dram 64 --l3 32 --l2 16 --l1 8 --policy LRU
```

### Available CLI arguments

| Argument   | Default | Description                          |
|------------|---------|--------------------------------------|
| `--ssd`    | 64      | SSD capacity (# instructions)        |
| `--dram`   | 32      | DRAM capacity (# instructions)       |
| `--l3`     | 16      | L3 cache capacity (# instructions)   |
| `--l2`     | 8       | L2 cache capacity (# instructions)   |
| `--l1`     | 4       | L1 cache capacity (# instructions)   |
| `--policy` | FIFO    | Cache policy: `FIFO`, `LRU`, `RANDOM`|

---

## Run Tests

```bash
cd Task3
pytest tests/ -v
```

---

## Project Structure

```
Task3/
├── README.md
├── ProcessorDesign-Task3.pdf
├── src/
│   ├── main.py                 # Entry point + CLI
│   └── memory_hierarchy.py     # Core simulation logic
└── tests/
    └── test_memory_hierarchy.py
```

---

## Program Output

1. Memory hierarchy configuration
2. Per-cycle instruction access trace
3. Data movement across levels (MOVE / STORE / EVICT)
4. Cache hits and misses per level
5. Hit ratio per level
6. Final contents of each memory level

---

## Cache Replacement Policies

| Policy | Description |
|--------|-------------|
| FIFO   | Evicts the oldest instruction first |
| LRU    | Evicts the least recently used instruction |
| RANDOM | Evicts a randomly selected instruction |

> SSD and DRAM always use FIFO. The chosen policy applies to L1, L2, and L3.

---

## Author

Your Name — Georgia State University CSC 4210/6210  
Spring Semester 2026
