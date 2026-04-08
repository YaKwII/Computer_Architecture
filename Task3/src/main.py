import argparse
from memory_hierarchy import MemoryHierarchy, ReplacementPolicy


def run_simulation(
    ssd_size:  int,
    dram_size: int,
    l3_size:   int,
    l2_size:   int,
    l1_size:   int,
    policy_str: str
) -> None:
    """Run the full memory hierarchy simulation."""

    # Map string -> enum
    policy_map = {
        "FIFO":   ReplacementPolicy.FIFO,
        "LRU":    ReplacementPolicy.LRU,
        "RANDOM": ReplacementPolicy.RANDOM,
    }
    policy = policy_map.get(policy_str.upper(), ReplacementPolicy.FIFO)

    sim = MemoryHierarchy(ssd_size, dram_size, l3_size, l2_size, l1_size, policy=policy)
    sim.print_config()

    # Pre-load 19 instructions into SSD
    for i in range(1, 20):
        sim.load_to_ssd(f"INSTR_{i:02d}")

    print("--- Starting Simulation ---")

    # Access pattern — notice INSTR_01, INSTR_03, INSTR_02 repeat (will hit cache)
    access_list = [1, 2, 3, 4, 5, 6, 1, 3, 7, 2]
    for instr_id in access_list:
        sim.access(f"INSTR_{instr_id:02d}")

    sim.print_state()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Memory Hierarchy Simulation — CSC 4210/6210 Task 3"
    )
    parser.add_argument("--ssd",    type=int, default=64,     help="SSD capacity (default: 64)")
    parser.add_argument("--dram",   type=int, default=32,     help="DRAM capacity (default: 32)")
    parser.add_argument("--l3",     type=int, default=16,     help="L3 cache capacity (default: 16)")
    parser.add_argument("--l2",     type=int, default=8,      help="L2 cache capacity (default: 8)")
    parser.add_argument("--l1",     type=int, default=4,      help="L1 cache capacity (default: 4)")
    parser.add_argument(
        "--policy",
        type=str,
        default="FIFO",
        choices=["FIFO", "LRU", "RANDOM"],
        help="Cache replacement policy for L1/L2/L3 (default: FIFO)"
    )

    args = parser.parse_args()

    run_simulation(
        ssd_size  = args.ssd,
        dram_size = args.dram,
        l3_size   = args.l3,
        l2_size   = args.l2,
        l1_size   = args.l1,
        policy_str = args.policy
    )


if __name__ == "__main__":
    main()
