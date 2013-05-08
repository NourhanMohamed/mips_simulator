import re, struct, string, bitstring, sys
from bitstring import BitArray

r_instructions = {
	"add":"0b100000", "sub":"0b100010", "sll":"0b000000", "srl":"0b000010", "and":"0b100100", "or":"0b100101",
	"nor":"0b100111", "slt":"0b101010", "jr":"0b001000"
}
i_instructions = {
	"addi":"0b001000", "andi":"0b001100", "ori":"0b001101", "beq":"0b000100" ,"bne":"0b000101", "lw":"0b100011",
	"lh":"0b100001", "lhu":"0b100101", "lb":"0b100000", "lbu":"0b100100", "sw":"0b101011", "sh":"0b101001",
	"sb":"0b101000", "lui":"0b001111"
}
j_instructions = {
	"j":"0b000010", "jal":"0b000011"
}
registers = {
	"$zero":"0b00000", "$at":"0b00001", "$v0":"0b00010", "$v1":"0b00011", "$a0":"0b00100", "$a1":"0b00101",
	"$a2":"0b00110", "$a3":"0b00111", "$t0":"0b01000", "$t1":"0b01001", "$t2":"0b01010", "$t3":"0b01011",
	"$t4":"0b01100", "$t5":"0b01101", "$t6":"0b01110", "$t7":"0b01111", "$s0":"0b10000", "$s1":"0b10001",
	"$s2":"0b10010", "$s3":"0b10011", "$s4":"0b10100", "$s5":"0b10101", "$s6":"0b10110", "$s7":"0b10111",
	"$t8":"0b11000", "$t9":"0b11001", "$k0":"0b11010", "$k1":"0b11011", "$gp":"0b11100", "$sp":"0b11101",
	"$fp":"0b11110", "$ra":"0b11111"
}
reg_file = []
for i in range(0,32):
	reg_file.append(0)

R_TYPE = 0
I_TYPE = 1
J_TYPE = 2
BIN = 3
INT = 4
HEX = 5

def control(operation):
	reg_dst = branch = mem_read = mem_to_reg = mem_write = reg_write = alu_src = jump = False
	alu_op = 0
	if operation in r_instructions:
		reg_dst = True

	if operation == "beq" or operation == "bne":
		branch = True

	if operation == "jal" or operation == "j" or operation == "jr":
		jump = True

	if operation == "lw" or operation == "lh" or operation == "lb" or operation == "lhu" or operation == "lbu":
		mem_read = True
		mem_to_reg = True

	if operation == "sw" or operation == "sh" or operation == "sb":
		mem_write = True

	if not branch or not jump or not mem_write:
		reg_write = True

	if not branch or not jump or not reg_dst:
		alu_src = True

	control_signals = { "RegDst":reg_dst, "Branch":branch, "MemRead":mem_read, "MemToReg":mem_to_reg,
	"MemWrite":mem_write, "RegWrite":reg_write, "ALUSrc":alu_src, "Jump":jump, "ALUOp":alu_op }
	return control_signals

def execute_rformat(txt_inst, operand1, operand2, shamt):
	result = 0
	if txt_inst == "add":
		result = operand1 + operand2
	elif txt_inst == "sub":
		result = operand1 - operand2
	elif txt_inst == "sll":
		result = operand1 * 2**shamt
	elif txt_inst == "srl":
		result = operand1 / 2**shamt
	elif txt_inst == "and":
		result = operand1 and operand2
	elif txt_inst == "or":
		result = operand1 or operand2
	elif txt_inst == "nor":
		result = not (operand1 or operand2)
	elif txt_inst == "slt":
		result = (0, 1)[operand1 > operand2]
	elif txt_inst == "jr":
		result = operand1
	return result

def execute_iformat(txt_inst, operand1, operand2, offset):
	result = 0
	if txt_inst == "addi" or txt_inst == "lw" or txt_inst == "lh" or txt_inst == "lb" \
		or txt_inst == "lhu" or txt_inst == "lbu" or txt_inst == "sw" or txt_inst == "sh" \
		or txt_inst == "sb":
		result = operand1 + offset
	elif txt_inst == "andi":
		result = operand1 & offset
	elif txt_inst == "ori":
		result = operand1 | offset
	elif txt_inst == "beq":
		result = (0, 1)[operand1 == operand2]
	elif txt_inst == "bne":
		result = (0, 1)[operand1 != operand2]
	return result

def fetch(address):
	print "Now Fetching..."
	instruction = inst_memory[address]

def decode(txt_instruction):
	txt_instruction = string.lower(txt_instruction)
	print "Decoding..."
	instruction = re.split("\s|,\s",txt_instruction)
	inst_type = None
	txt_op = instruction[0]
	try:
		instruction[0] = r_instructions[instruction[0]]
		inst_type = R_TYPE
	except KeyError:
		try:
			instruction[0] = i_instructions[instruction[0]]
			inst_type = I_TYPE
		except KeyError:
			try:
				instruction[0] = j_instructions[instruction[0]]
				inst_type = J_TYPE
			except KeyError:
				print "Invalid instruction!"
				instruction[0] = None

	if not instruction[0]:
		return

	control_signals = control(txt_op)
	bool_to_signal = { True:1, False:0 }
	print "Generating control signals..."
	print "RegDst = %i" % bool_to_signal[control_signals["RegDst"]]
	print "Branch = %i" % bool_to_signal[control_signals["Branch"]]
	print "Jump = %i" % bool_to_signal[control_signals["Jump"]]
	print "MemRead = %i" % bool_to_signal[control_signals["MemRead"]]
	print "MemWrite = %i" % bool_to_signal[control_signals["MemWrite"]]
	print "MemToReg = %i" % bool_to_signal[control_signals["MemToReg"]]
	print "RegWrite = %i" % bool_to_signal[control_signals["RegWrite"]]
	print "ALUSrc = %i" % bool_to_signal[control_signals["ALUSrc"]]
	print "ALUOp = %i" % control_signals["ALUOp"]

	if inst_type == R_TYPE:
		opcode = 0
		shamt = 0
		function = int(instruction[0], 2)
		rs = hex(int(registers[instruction[2]], 2))
		rt = hex(int(registers[instruction[3]], 2))
		rd = hex(int(registers[instruction[1]], 2))
		if function == 0 or function == 2:
			shamt = rt
			rt = 0
		print "Opcode is %i, Function is %i, Source1 is %s, Source2 is %s, Dest is %s, Shamt is %s" % (
		opcode,function,rs,rt,rd,shamt)
		result = execute_rformat(txt_op, reg_file[int(rs,16)], reg_file[int(rt,16)], shamt)
	elif inst_type == I_TYPE:
		opcode = int(instruction[0], 2)
		if re.match("\d+\(\$[a-z]\d\)", instruction[2]):
			off = re.match('\d+', instruction[2]).group()
			offset = int(off)
			if offset%4 != 0:
				print "Terminating... Invalid Offset!"
				return
			rs = hex(int(registers[instruction[2][len(off)+1:len(off)+4]], 2))
		else:
			rs = hex(int(registers[instruction[2]], 2))
			offset = int(instruction[3])
		rt = hex(int(registers[instruction[1]], 2))
		print "Opcode is %i, Source1 is %s, Dest is %s, Offset is %i" % (opcode,rs,rt,offset)
		result = execute_iformat(txt_op, reg_file[int(rs,16)], reg_file[int(rt,16)], offset)
	elif inst_type == J_TYPE:
		opcode = int(instruction[0], 2)
		if opcode == 3:
			pc_relative = int(instruction[0],2) * 4
			j_address = "0b1111" + bin(pc_relative)[2:]
		elif opcode == 2:
			j_address = hex(int(instruction[0],2))
		print "Opcode is %i, Address %s" % (opcode,j_address)

		# value = struct.unpack(">h", s) for getting 16 bits from 32!

main_memory = {}

# sw: store 32 bits in 4 consecutive addresses (big endian)
# sh: store rightmost 16 bits in 2 consecutive addresses (big endian)

def memory(address, txt_inst, control_signals, write_val=None, reg_to_write=None):
  if control_signals["MemWrite"]:
    if write_val != None:
      print "writing to memory ..."
      memory_write(address, txt_inst, write_val)
    else:
      print "cannot write a none value to the memory"
  elif control_signals["MemRead"]:
    if reg_to_write != None:
      print "Reading from memory ..."
    else:
      print "cannot load into an unspecified register"
  return

def memory_write(address, txt_inst, write_val):
  if txt_inst == "sw":
    address = complete_address(address)
    main_memory[address] = write_val[0:8]
    address_1 = bin(int(address, 2) + 1)
    address_1 = complete_address(address_1)
    print address_1
    main_memory[address_1] = write_val[8:16]
    print main_memory.items()
    address_2 = bin(int(address_1, 2) + 1)
    address_2 = complete_address(address_2)
    main_memory[address_2] = write_val [16:24]
    print main_memory.items()
    address_3 = bin(int(address_2, 2) + 1)
    address_3 = complete_address(address_3)
    main_memory[address_3] = write_val[24:32]
    print main_memory.items()
  elif txt_inst == "sh":
    address = complete_address(address)
    main_memory[address] = write_val [16:24]
    print main_memory.items()
    address_1 = bin(int(address, 2) + 1)
    address_1 = complete_address(address_1)
    main_memory[address_1] = write_val[24:32]
    print main_memory.items()
  elif txt_inst == "sb":
    address = complete_address(address)
    main_memory[address] = write_val[24:32]
    print main_memory.items()

def memory_read(address, txt_inst, reg_to_write):
  value = 'none'
  if txt_inst == "lw":
    address = complete_address(address)
    address_1 = bin(int(address, 2) + 1)
    address_1 = complete_address(address_1)
    address_2 = bin(int(address_1, 2) + 1)
    address_2 = complete_address(address_2)
    address_3 = bin(int(address_2, 2) + 1)
    address_3 = complete_address(address_3)
    if main_memory.has_key(address) and main_memory.has_key(address_1) \
    	and main_memory.has_key(address_2) and main_memory.has_key(address_3):
      a = main_memory[address]
      b = main_memory[address_1]
      c = main_memory[address_2]
      d = main_memory[address_3]
      value = ''.join((a,b,c,d))
      value = binary_to_int(value)
  elif txt_inst == "lhu":
    address = complete_address(address)
    address_1 = bin(int(address, 2) + 1)
    address_1 = complete_address(address_1)
    if main_memory.has_key(address) and main_memory.has_key(address_1):
      a = '0000000000000000'
      b = main_memory[address]
      c = main_memory[address_1]
      value = ''.join((a,b,c))
      value = binary_to_int(value)
  elif txt_inst == "lbu":
    address = complete_address(address)
    if main_memory.has_key(address):
      a = '000000000000000000000000'
      b = main_memory[address]
      value = ''.join((a,b))
      value = binary_to_int(value)
  elif txt_inst == "lb":
    address = complete_address(address)
    if main_memory.has_key(address): 
      b = main_memory[address]
      if b[0] == 1:
        a = '111111111111111111111111'
        value = ''.join((a,b))
        value = binary_to_int(value)
      else:
        a = '000000000000000000000000'
        value = ''.join((a,b))
        value = binary_to_int(value)
  elif txt_inst == "lh":
    address = complete_address(address)
    address_1 = bin(int(address, 2) + 1)
    address_1 = complete_address(address_1)
    if main_memory.has_key(address) and main_memory.has_key(address_1):
      b = main_memory[address]
      c = main_memory[address_1]
      if b[0] == 1:
        a = '1111111111111111'
        value = ''.join((a,b,c))
        value = binary_to_int(value)
      else:
        a = '0000000000000000'
        value = ''.join((a,b,c))
        value = binary_to_int(value)
  elif txt_inst == "lui":
        a = immediate_value
        b = '0000000000000000'
        value = ''.join((a,b))
        value = binary_to_int(value)
  write_back(value, reg_to_write)

# write back the value in the specified register
def write_back(value, reg_to_write):
  print value
  if reg_to_write == 0:
  	print "cannot write to register 0"
  else:
  	reg_file[reg_to_write] = value
  return

# to always make sure the address is in the right format 
def complete_address(value):
  updated_value = value[2:]
  length = len(updated_value)
  if length > 32 or length == 0:
    return 'none'
  elif length == 32:
    return updated_value
  else:
    limit = 32-length
    value = str(updated_value)
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

decode('sw $s1, 102($s0)')

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: %s <file name>" % sys.argv[0]
  else:
    f = open(sys.argv[1])
    instructions = f.readlines()
    # intrauctions is now a list of text instractions
    # call main function here

#ALUOp still missing
#jal pc relative concat still missing
