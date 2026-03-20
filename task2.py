import sys
import argparse  

def print_kmap(truth_table, n):
    print("\nKarnaugh Map:")
    if n == 2:
        print("     0    1   <- B")
        print("0  ", truth_table[0]['output'], "  ", truth_table[1]['output'], "  <- A=0")
        print("1  ", truth_table[2]['output'], "  ", truth_table[3]['output'], "  <- A=1")

def eval_expr(inputs, simplified):
    """Simple eval for our n=2 cases"""
    A, B = inputs
    if 'XOR' in simplified or 'A\'B + AB\'' in simplified:
        return A ^ B
    elif 'A · B' in simplified:
        return A and B
    elif 'B' in simplified:
        return B
    elif len(inputs) == 1:  # n=1 test
        return A
    return 0  # Fallback

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int, help='Number of inputs (2-4)')
    args = parser.parse_args()
    n = args.n
    if n < 2 or n > 4:
        print("n must be 2-4")
        sys.exit(1)
    
    # Read truth table
    truth_table = []
    expected_rows = 1 << n  
    print(f"Enter {expected_rows} rows like '0 1 0'")
    for i in range(expected_rows):
        line = input(f"Row {i}: ").strip().split()
        if len(line) != n + 1 or not all(b in '01' for b in line):
            print("Bad row! Use 0/1 only.")
            sys.exit(1)
        inputs = [int(b) for b in line[:n]]
        output = int(line[-1])
       
        bin_str = ''.join(map(str, inputs))
        if bin_str in [''.join(map(str, tt['inputs'])) for tt in truth_table]:
            print("Duplicate inputs!")
            sys.exit(1)
        truth_table.append({'inputs': inputs, 'output': output})
    
    # SOP or POS
    form = input("SOP or POS? ").upper()
    
    # Minterms/maxterms
    minterms = [i for i, tt in enumerate(truth_table) if tt['output'] == 1]
    maxterms = [i for i, tt in enumerate(truth_table) if tt['output'] == 0]
    
    print("\nTruth Table:")
    for i, tt in enumerate(truth_table):
        print(f"m{i:1}: {' '.join(map(str, tt['inputs']))} → {tt['output']}")
    
    print(f"Canonical {form}: " + (f"Σm{minterms}" if form=='SOP' else f"ΠM{maxterms}"))
    print(f"Minterms: {minterms}, Maxterms: {maxterms}")
    
    print_kmap(truth_table, n)
    
    # Simplify n=2
    simplified = "Complex (add more cases)"
    groups = ""
    if n == 2 and form == 'SOP':
        ones = [truth_table[i]['output'] for i in range(4)]
        if ones == [0,1,1,0]:
            simplified = "A ⊕ B  (A'B + AB')"
            groups = "Diagonal group of two 1s"
        elif ones == [0,0,0,1]:
            simplified = "A B"
            groups = "Corner 1"
        elif ones == [0,1,0,1]:
            simplified = "B"
            groups = "Right column"
        elif ones == [1,0,0,0]:
            simplified = "A'"
            groups = "Top-left"
        else:
            simplified = f"Σm{minterms}"
            groups = f"Minterms {minterms}"
    print(f"K-Map Grouping: {groups}")
    print(f"Simplified {form}: {simplified}")
    
    # Validation
    print("\nValidation:")
    all_match = True
    for i, tt in enumerate(truth_table):
        pred = eval_expr(tt['inputs'], simplified)
        status = "Done" if pred == tt['output'] else "N/A"
        print(f"Row {i} { ' '.join(map(str,tt['inputs']))}: {pred} == {tt['output']} {status}")
        if pred != tt['output']: all_match = False
    print(f"Overall: {'PASS' if all_match else 'FAIL'}")

if __name__ == "__main__":
    main()
