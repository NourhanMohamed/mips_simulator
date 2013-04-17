import re
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

R_TYPE = 0
I_TYPE = 1
J_TYPE = 2

def fetch(address):
	print "Now Fetching..."
	instruction = inst_memory[address]

def decode(txt_instruction):
	print "Decoding..."
	instruction = re.split('\s|,\s',txt_instruction)
	inst_type = None
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
	elif inst_type == I_TYPE:
		opcode = int(instruction[0], 2)
		rs = hex(int(registers[instruction[2]], 2))
		rt = hex(int(registers[instruction[1]], 2))
		offset = int(instruction[3])
		print "Opcode is %i, Source1 is %s, Dest is %s, Offset is %i" % (opcode,rs,rt,offset)
	elif inst_type == J_TYPE:
		opcode = int(instruction[0], 2)
		pc_relative = int(instruction[0],2) * 4
		j_address = '0b1111' + bin(pc_relative)[2:]
		print "Opcode is %i, Address %s" % (opcode,j_address)

def execute:
	
decode('j 0b10')
	