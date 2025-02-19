import sys

# print("Assembler")

registers = {
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

    'jal':  {'type': 'J', 'opcode': '1101111'}
}


def error_R(op, rd, rs1, rs2):
    if op not in opcode_table:
        # print("Wrong instruction")
        return False
    if rd not in registers or rs1 not in registers or rs2 not in registers:
        # print("Wrong register")
        return False
    return True


def error_I(op, rd, rs1, imm):
    if op not in opcode_table:
        # print("Wrong instruction")
        return False
    if rd not in registers or rs1 not in registers:
        # print("Wrong register")
        return False
    try:
        int(imm)
    except ValueError:
        # print("Wrong immediate value")
        return False
    return True


def error_S(op, rs1, rs2, imm):
    if op not in opcode_table:
        # print("Wrong instruction")
        return False
    if rs1 not in registers or rs2 not in registers:
        # print("Wrong register")
        return False
    try:
        int(imm)
    except ValueError:
        # print("Wrong immediate value")
        return False
    return True


def error_B(op, rs1, rs2, imm):
    if op not in opcode_table:
        # print("Wrong instruction")
        return False
    if rs1 not in registers or rs2 not in registers:
        # print("Wrong register")
        return False
    try:
        int(imm)
    except ValueError:
        # print("Wrong immediate value")
        return False
    return True


def error_J(op, rd, imm):
    if op not in opcode_table:
        # print("Wrong instruction")
        return False
    if rd not in registers:
        # print("Wrong register")
        return False
    try:
        int(imm)
    except ValueError:
        # print("Wrong immediate value")
        return False
    return True


def labelfinding(lines):
    labels = {}
    pc = 0
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if ':' in l:
            label, remaining = l.split(':')
            label = label.strip()
            remaining = remaining.strip()
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
# convert immediate to 12-bit binary


def encode_R(op, rd, rs1, rs2):
    if not (error_R(op, rd, rs1, rs2)):
        raise ValueError("Wrong Instruction")
    f7f3op = opcode_table[op]
    return f"{f7f3op['funct7']}{registers[rs2]}{registers[rs1]}{f7f3op['funct3']}{registers[rd]}{f7f3op['opcode']}"


def encode_I(op, rd, rs1, imm):
    if not (error_I(op, rd, rs1, imm)):
        raise ValueError("Wrong Instruction")
    f3op = opcode_table[op]
    imm = encode_imm(imm)
    return f"{imm}{registers[rs1]}{f3op['funct3']}{registers[rd]}{f3op['opcode']}"


def encode_S(op, rs1, rs2, imm):
    if not (error_S(op, rs1, rs2, imm)):
        raise ValueError("Wrong Instruction")
    f3op = opcode_table[op]
    imm = encode_imm(imm)
    return f"{imm[0:7]}{registers[rs2]}{registers[rs1]}{f3op['funct3']}{imm[7:]}{f3op['opcode']}"


def encode_B(op, rs1, rs2, imm):
    if not (error_B(op, rs1, rs2, imm)):
        raise ValueError("Wrong Instruction")
    f3op = opcode_table[op]
    imm = int(imm)
    if imm < 0:
        imm = (1 << 13) + imm
    imm = f"{imm & 0x1FFF:013b}"

    return f"{imm[0]}{imm[2:8]}{registers[rs2]}{registers[rs1]}{f3op['funct3']}{imm[8:12]}{imm[1]}{f3op['opcode']}"


def encode_J(op, rd, imm):
    if not (error_J(op, rd, imm)):
        raise ValueError("Wrong Instruction")
    op = opcode_table[op]
    imm = int(imm)
    # imm+=4
    if imm < 0:
        imm = (1 << 21) + imm
    imm = f"{imm & 0x1FFFFE:021b}"
    # print(imm)

    return f"{imm[0]}{imm[10:20]}{imm[9]}{imm[1:9]}{registers[rd]}{op['opcode']}"




def run(lines):
    labels = labelfinding(lines)
    pc = 0
    b = ""
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if ':' in l:
            label, remaining = l.split(':')
            instruction = remaining.strip()
        else:
            instruction = l
        operation, remaining = instruction.split(" ")
        operation = operation.strip()
        remaining = remaining.strip()

        if operation in opcode_table:
            if opcode_table[operation]['type'] == 'R':
                # print("R")
                rd, rs1, rs2 = remaining.split(",")
                # print(encode_R(operation, rd, rs1, rs2))
                b += encode_R(operation, rd, rs1, rs2)

            elif opcode_table[operation]['type'] == 'I':
                # print("I")
                if operation == 'lw':

                    rd, remaining = remaining.split(",")
                    remaining = remaining.strip()
                    imm, rs1 = remaining.split("(")
                    imm = imm.strip()
                    rs1 = rs1[:-1]
                    rs1 = rs1.strip()

                    if imm in labels:
                        imm = labels[imm] - pc
                    # print(encode_I(operation, rd, rs1, imm))
                    b += encode_I(operation, rd, rs1, imm)
                else:
                    rd, rs1, imm = remaining.split(",")
                    if imm in labels:
                        imm = labels[imm] - pc
                    # print(encode_I(operation, rd, rs1, imm))
                    b += encode_I(operation, rd, rs1, imm)

            elif opcode_table[operation]['type'] == 'S':
                # print("S")
                rs2, remaining = remaining.split(",")
                remaining = remaining.strip()
                imm, rs1 = remaining.split("(")
                imm = imm.strip()
                rs1 = rs1[:-1]
                rs1 = rs1.strip()

                if imm in labels:
                    imm = labels[imm] - pc
                # print(encode_S(operation, rs1, rs2, imm))
                b += encode_S(operation, rs1, rs2, imm)
            elif opcode_table[operation]['type'] == 'B':
                # print("B")

                rs1, rs2, imm = remaining.split(",")
                if imm in labels:
                    imm = labels[imm] - pc
                # print(encode_B(operation, rs1, rs2, imm))
                b += encode_B(operation, rs1, rs2, imm)

            elif opcode_table[operation]['type'] == 'J':
                # print("J")
                rd, imm = remaining.split(",")
                if imm in labels:

                    imm = labels[imm] - pc
                # print("imm: ", imm, " pc:", pc)
                # print(encode_J(operation, rd, imm))
                b += encode_J(operation, rd, imm)
            pc += 4
            b += "\n"

    return b

def main(inp, out):
    # inp = r'C:\Users\amrit\Documents\co\co-assignment\SimpleAssembler\a.txt'
    with open(inp, "r") as f:
        l = f.readlines()
        l = [x.strip() for x in l]
        l = [x for x in l if x]
        if l[-1] != 'beq zero,zero,0':
            raise ValueError("Last line should be Virtual Halt")
    # print(l)

    # print(labelfinding(l))

    
    me = run(l)
    # print()
    me = me.strip()
    me = me.split("\n")
    me = [x.strip() for x in me]
    me = [x for x in me if x]

    
    # out = r'C:\Users\amrit\Documents\co\co-assignment\SimpleAssembler\b.txt'
    with open(out, "w") as f:
        for i in me:
            f.write(i)
            f.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        # print("Usage: python Assembler.py <input_file> <output_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    print(input_file)
    print( output_file)
    main(input_file, output_file)
    
