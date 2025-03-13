#import sys

print("Sim")

registers = {
    '00000': 'zero', '00001': 'ra', '00010': 'sp', '00011': 'gp',
    '00100': 'tp', '00101': 't0', '00110': 't1', '00111': 't2',
    '01000': 's0', '01001': 's1', '01010': 'a0', '01011': 'a1',
    '01100': 'a2', '01101': 'a3', '01110': 'a4', '01111': 'a5',
    '10000': 'a6', '10001': 'a7', '10010': 's2', '10011': 's3',
    '10100': 's4', '10101': 's5', '10110': 's6', '10111': 's7',
    '11000': 's8', '11001': 's9', '11010': 's10', '11011': 's11',
    '11100': 't3', '11101': 't4', '11110': 't5', '11111': 't6'
}

reg_values = {reg: 0 for reg in registers.keys()}
mem_values = {"0x"+f"{loc:08x}".upper(): 0 for loc in range(65536, 65660 + 1, 4)}

opcode_table = {
    '0110011': { 
        '0000000': {
            '000': 'add',
            '010': 'slt',
            '101': 'srl',
            '110': 'or',
            '111': 'and'
        },
        '0100000': {
            '000': 'sub'
        }
    },
    '0000011': {
        '': {
            '010': 'lw'
        }
    },
    '0010011': {
        '': {
            '000': 'addi'
        }
    },
    '1100111': {
        '': {
            '000': 'jalr'
        }
    },
    '0100011': {
        '': {
            '010': 'sw'
        }
    },
    '1100011': {
        '': {
            '000': 'beq',
            '001': 'bne',
            '100': 'blt'
        }
    },
    '1101111': {
        '': {
            '': 'jal'
        }
    }
}


def checkR(opcode,f7,f3):
    if f7 in opcode_table[opcode] and f3 in opcode_table[opcode][f7]:
        return True
    else:
        raise ValueError("UNKNOWN FUNCTION")

def checkS(opcode, f3):
    if '' in opcode_table[opcode] and f3 in opcode_table[opcode]['']:
        return True
    else:
        raise ValueError("UNKNOWN FUNCTION")

def checkB(opcode, f3):
    if '' in opcode_table[opcode] and f3 in opcode_table[opcode]['']:
        return True
    else:
        raise ValueError("UNKNOWN FUNCTION")

def checkI(opcode, f3):
    if '' in opcode_table[opcode] and f3 in opcode_table[opcode]['']:
        return True
    else:
        raise ValueError("UNKNOWN FUNCTION")

type_table={'0110011':'R',
            
            '0000011':'I',
            '0010011':'I',
            '1100111':'I',
            
            '0100011':'S',
            
            '1100011':'B',
            
            '1101111':'J'
}


def run(l):
    l = [x.strip() for x in l]
    l = [x for x in l if x]
    print(l)

    pc=0
    for line in l:
        opcode=line[-7:]
        if opcode not in opcode_table:
            raise ValueError("UNKNOWN OPCODE")
        it=type_table[opcode]
        if it=='R':
            f7=line[:7]
            rs2=line[7:12]
            rs1=line[12:17]
            f3=line[17:20]
            rd=line[20:25]
            assert checkR(opcode,f7,f3)
            assert rs1 in registers
            assert rs2 in registers
            assert rd in registers
            

        elif it=='I':
            imm=line[:12]
            rs1=line[12:17]
            f3=line[17:20]
            rd=line[20:25]
            assert checkI(opcode,f3)
            assert rs1 in registers
            
        elif it=='S':
            imm=line[:7]+line[20:25]
            rs2=line[7:12]
            rs1=line[12:17]
            f3=line[17:20]
            assert checkS(opcode,f3)
            assert rs1 in registers
            assert rs2 in registers
            
        elif it=='B':
            imm=line[0]+line[24]+line[1:7]+line[20:24]
            rs2=line[7:12]
            rs1=line[12:17]
            f3=line[17:20]
            assert checkB(opcode,f3)
            assert rs1 in registers
            assert rs2 in registers
            
        elif it=='J':
            imm=line[0]+line[12:20]+line[11]+line[1:11]
            rd=line[20:25]
            assert rd in registers
            
        else:
            raise ValueError("UNKNOWN OPCODE")
            

        print(it)


    
inp="bin.txt"
with open(inp, "r") as f:
    l = f.readlines()
run(l)