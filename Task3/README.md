# Processor Design Task 3 — Memory Hierarchy Simulation

## Overview
Simulates SSD → DRAM → L3 → L2 → L1 → CPU memory hierarchy.  
Data moves one level at a time. No bypassing allowed.  
All data treated as 32-bit instructions.

## How to Run
1. Open terminal in the `Task3/` folder
2. Run:
```
python src/main.py
```

## Configuration
Edit the sizes at the top of `src/main.py`:
- `ssd_size`, `dram_size`, `l3_size`, `l2_size`, `l1_size`
- Rule enforced: SSD > DRAM > L3 > L2 > L1

## Features
- Clock-driven simulation
- FIFO cache eviction policy
- Read (fetch) and write-back operations
- Cache hit/miss tracking
- Instruction access trace printed per clock cycle
- Final state of all memory levels printed at end

## Program Output
1. Memory hierarchy configuration
2. Per-cycle instruction access trace
3. Data movement across levels
4. Cache hits and misses
5. Final state of each memory level

## Project Structure
```
Task3/
├── README.md
└── src/
    ├── main.py
    └── memory_hierarchy.py
```

## Author
Michael Powers — Georgia State University CSC 4210/6210  
Spring Semester 2026
