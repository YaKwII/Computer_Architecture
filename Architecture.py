# CSC 4210/6210 Computer Architecture - Spring 2026
# Michael Powers
# Submission: GitHub link

MIN_INT32 = -2**31 
MAX_INT32 = 2**31 - 1  

def decimal_to_twos_complement(n, bits=32):
    if n < 0:
        n = (1 << bits) + n
    return format(n & ((1 << bits) - 1), f'0{bits}b')

def twos_complement_to_decimal(binary_str):
    bits = len(binary_str)
    n = int(binary_str, 2)
    if n >= (1 << (bits - 1)):
        n -= (1 << bits)
    return n

def binary_to_hex(binary_str):
    return format(int(binary_str, 2), '08X')

def convert_number(decimal_input, output_format):
    try:
        x = int(decimal_input)
    except ValueError:
        return "Invalid input", 0, 0
    
    overflow = 0
    saturated = 0
    
    # FR4-FR5: Overflow detection and saturation
    if x < MIN_INT32:
        overflow = 1
        saturated = 1
        internal_value = MIN_INT32
    elif x > MAX_INT32:
        overflow = 1
        saturated = 1
        internal_value = MAX_INT32
    else:
        internal_value = x
    
    # FR3: Convert to internal 32-bit Two's Complement
    binary_str = decimal_to_twos_complement(internal_value)
    
    # FR6: Output formatting
    if output_format.upper() == 'DEC':
        value_out = str(internal_value)
    elif output_format.upper() == 'BIN':
        value_out = binary_str
    elif output_format.upper() == 'HEX':
        value_out = binary_to_hex(binary_str)
    else:
        return "Invalid format", 0, 0
    
    return value_out, overflow, saturated



# Example invocations
print(convert_number("123", "DEC"))   
print(convert_number("0", "BIN"))     
print(convert_number("-123", "HEX"))  




# Comprehensive test suite
test_cases = [
    ("123", "DEC"),     
    ("0", "BIN"),        
    ("-123", "HEX"),     
    (str(MAX_INT32), "BIN"),  
    (str(MIN_INT32), "DEC"),  
    (str(MAX_INT32 + 1), "DEC"),  
    (str(MIN_INT32 - 1), "HEX")   
]

print("Test Results:")
for decimal, fmt in test_cases:
    result = convert_number(decimal, fmt)
    print(f"Input: {decimal} -> {fmt}: {result}")
