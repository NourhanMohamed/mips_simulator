import bitstring
from bitstring import BitArray
# to always make sure the address is in the right format  
def complete_address(value):
  length = len(value)
  if length > 32 or length == 0:
    return 'none' 
  elif length == 32:
    return value
  else: 
    limit = 32-length
    value = str(value)
    for x in range(0, limit):
      value = ''.join(('0',value))
    return value

# to transform the integer to binary string of 32 bits to be written in memory
def value_to_write(value):
  b = BitArray(int=value, length=32)
  b = b.bin
  return b

# transform binary string loaded from memory to int 
def binary_to_int(value):
  a = BitArray(bin= value)
  a = a.int 
  return a

def binary_or_int_to_hex(value, type):
  if type == BIN: #binary_to_hex
    a = hex(int(value, 2))
    return a 
  elif type == INT: #int_to_hex
    a = hex(value)
    return a 

def hex_to_binary_or_int(value, type):
  if type == INT:
    a = int(value, 16)
    return a 
  elif type == BIN:
    a = bin(int('0xa', 16))
    return a