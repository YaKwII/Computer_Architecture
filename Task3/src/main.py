from memory_hierarchy import MemoryHierarchy

def main():
    print("=== Memory Hierarchy Simulation ===")
    print()

    # Configure sizes (in number of 32-bit instructions)
    ssd_size  = 64
    dram_size = 32
    l3_size   = 16
    l2_size   = 8
    l1_size   = 4

    sim = MemoryHierarchy(ssd_size, dram_size, l3_size, l2_size, l1_size)

    # Print starting config
    sim.print_config()

    # Load some instructions into SSD
    for i in range(1, 20):
        sim.load_to_ssd(f"INSTR_{i:02d}")

    print("\n--- Starting Simulation ---\n")

    # Access instructions (triggers movement through hierarchy)
    access_list = [1, 2, 3, 4, 5, 6, 1, 3, 7, 2]
    for instr_id in access_list:
        sim.access(f"INSTR_{instr_id:02d}")

    print("\n--- Final State ---")
    sim.print_state()

if __name__ == "__main__":
    main()
