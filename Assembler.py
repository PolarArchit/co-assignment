print("Assember")

registers={
    'zero': '00000', 'ra': '00001', 'sp': '00010', 'gp': '00011',
    'tp': '00100', 't0': '00101', 't1': '00110', 't2': '00111',
    's0': '01000', 's1': '01001', 'a0': '01010', 'a1': '01011',
    'a2': '01100', 'a3': '01101', 'a4': '01110', 'a5': '01111',
    'a6': '10000', 'a7': '10001', 's2': '10010', 's3': '10011',
    's4': '10100', 's5': '10101', 's6': '10110', 's7': '10111',
    's8': '11000', 's9': '11001', 's10': '11010', 's11': '11011',
    't3': '11100', 't4': '11101', 't5': '11110', 't6': '11111'
}

opcode_table = {
    'add':  {'type': 'R', 'funct7': '0000000', 'funct3': '000', 'opcode': '0110011'},
    'sub':  {'type': 'R', 'funct7': '0100000', 'funct3': '000', 'opcode': '0110011'},
    'slt':  {'type': 'R', 'funct7': '0000000', 'funct3': '010', 'opcode': '0110011'},
    'srl':  {'type': 'R', 'funct7': '0000000', 'funct3': '101', 'opcode': '0110011'},
    'or':   {'type': 'R', 'funct7': '0000000', 'funct3': '110', 'opcode': '0110011'},
    'and':  {'type': 'R', 'funct7': '0000000', 'funct3': '111', 'opcode': '0110011'},
    
    'lw':   {'type': 'I', 'funct3': '010', 'opcode': '0000011'},
    'addi': {'type': 'I', 'funct3': '000', 'opcode': '0010011'},
    'jalr': {'type': 'I', 'funct3': '000', 'opcode': '1100111'},
    
    'sw':   {'type': 'S', 'funct3': '010', 'opcode': '0100011'},
    
    'beq':  {'type': 'B', 'funct3': '000', 'opcode': '1100011'},
    'bne':  {'type': 'B', 'funct3': '001', 'opcode': '1100011'},
    'blt':  {'type': 'B', 'funct3': '100', 'opcode': '1100011'},
    'bge':  {'type': 'B', 'funct3': '101', 'opcode': '1100011'},

    'jal':  {'type': 'J', 'opcode': '1101111'}
}

def initialpass(lines):
    labels = {}
    pc = 0
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if ':' in l:
            label,remaining = l.split(':')
            label=label.strip()
            remaining=remaining.strip()
            labels[label] = pc
            if remaining:
                pc += 4
        else:
            pc += 4
    return labels

def encode_imm(imm):
    imm = int(imm)
    if imm < 0:
        imm = (1 << 12) + imm
    imm = f"{imm & 0xFFF:012b}"
    return imm
#convert immediate to 12-bit binary

def encode_R(op, rd, rs1, rs2):
    f7f3op = opcode_table[op]
    return f"{f7f3op['funct7']}{registers[rs2]}{registers[rs1]}{f7f3op['funct3']}{registers[rd]}{f7f3op['opcode']}"

def encode_I(op, rd, rs1, imm):
    f3op = opcode_table[op]
    imm = encode_imm(imm)
    return f"{imm}{registers[rs1]}{f3op['funct3']}{registers[rd]}{f3op['opcode']}"

def encode_S(op, rs1, rs2, imm):
    f3op = opcode_table[op]
    imm = encode_imm(imm)
    return f"{imm[0:7]}{registers[rs2]}{registers[rs1]}{f3op['funct3']}{imm[7:]}{f3op['opcode']}"

def encode_B(op, rs1, rs2, imm):
    f3op = opcode_table[op]
    imm = int(imm)
    if imm < 0:
        imm = (1 << 13) + imm
    imm = f"{imm & 0x1FFF:013b}"

    return f"{imm[0]}{imm[2:8]}{registers[rs2]}{registers[rs1]}{f3op['funct3']}{imm[8:12]}{imm[1]}{f3op['opcode']}"

def encode_J(op, rd, imm):
    op = opcode_table[op]
    imm = int(imm)
    if imm < 0:
        imm = (1 << 21) + imm
    imm = f"{imm & 0x1FFFFF:021b}"
    
    return f"{imm[0]}{imm[10:20]}{imm[9]}{imm[1:9]}{registers[rd]}{op['opcode']}"