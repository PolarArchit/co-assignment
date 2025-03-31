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

reg_values = {reg: '0'*32 for reg in registers.keys()}
reg_values['00010']='00000000000000000000000101111100'

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
        '': 'jal'
    }
}

def copytofile(pc):
    string = ""
    string += format(pc, '#034b')
    for i in reg_values:
        string += ' '
        string += '0b' + i
    string += '\n'
    return string

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
def checkJ(opcode):
    if '' in opcode_table[opcode]:
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


def signed_comparison(a,b):
    if a[0]=='1':
        value_a=-(2**31)+int(a[1:32], 2)
    else:
        value_a=int(a[0:32], 2)
    if b[0]=='1':
        value_b=-(2**31)+int(b[1:32], 2)
    else:
        value_b=int(b[0:32], 2)
    if value_a<value_b:
        return True
    return False
    
#signed extension function
def sign_extension(a):
    if a[0]=='0':
        a = '0'*(32-len(a))+a
    elif a[0]=='1':
        a = '1'*(32-len(a))+a
    return a

#function that represent decimal value in 2s complement notation
def sign_rep(a):
    if a[0]=='0':
        a=int(a[0:len(a)], 2)
    elif a[0]=='1':
        a=-(2**(len(a)-1))+int(a[1:32], 2)
    return a
def R_execute(opcode,f7,rs2,rs1,f3,rd):
    if opcode_table[opcode][f7][f3]=='add':
        reg_values[rd] = int(reg_values[rs1],2) + int(reg_values[rs2],2)
        reg_values[rd] = bin(reg_values[rd] & 0xFFFFFFFF)[2:]
        reg_values[rd]=reg_values[rd].zfill(32)

    
    elif opcode_table[opcode][f7][f3]=='slt':
        if signed_comparison(reg_values[rs1],reg_values[rs2])==True:
            reg_values[rd]='00000000000000000000000000000001'

    elif opcode_table[opcode][f7][f3]=='srl':

        value = reg_values[rs2][27:32]
        value  = int(value, 2)
        print(value)
        reg_values[rd]=reg_values[rs1][0:(32-value)]
        reg_values[rd]='0'*value+reg_values[rd]

    elif opcode_table[opcode][f7][f3]=='or':
        final=[]
        for i in range(32):
            if reg_values[rs1][i]=='1' or reg_values[rs2][i]=='1':
                final.append('1')
            elif reg_values[rs1][i]=='0' and reg_values[rs2][i]=='0':
                final.append('0')
        final = ''.join(final)
        reg_values[rd]=final
    elif opcode_table[opcode][f7][f3]=='and':
        final=[]
        for i in range(32):
            if reg_values[rs1][i]=='1' and reg_values[rs2][i]=='1':
                final.append('1')
            elif reg_values[rs1][i]=='0' or reg_values[rs2][i]=='0':
                final.append('0')
        final = ''.join(final)
        reg_values[rd]=final
    elif opcode_table[opcode][f7][f3]=='sub':
        reg_values[rd] = int(reg_values[rs1],2) - int(reg_values[rs2],2)
        reg_values[rd] = bin(reg_values[rd] & 0xFFFFFFFF)[2:]
        reg_values[rd]=reg_values[rd].zfill(32)

def J_execute(opcode, imm, rd, PC):
    if opcode_table[opcode][''] == 'jal':
        imm = int(imm, 2)
        if (imm >> 20) & 1:
            imm = imm - (1 << 21)  
        reg_values[rd] = format(PC + 4, '032b')  
        PC = PC + imm
        return PC
    return reg_values[rd]

def I_execute(imm, rs1 ,f3, rd,opcode,pc):
    if opcode_table[opcode][''][f3] == 'addi':
        imm = int(sign_extension(imm), 2) if imm[0] == '0' else int(sign_extension(imm), 2) - (1 << 32)
        reg_values[rd] = int(reg_values[rs1], 2) + imm
        reg_values[rd] = format(reg_values[rd] & 0xFFFFFFFF, '032b')
        return pc + 4
    if opcode_table[opcode][''][f3] == 'jalr':
        imm = int(sign_extension(imm), 2) if imm[0] == '0' else int(sign_extension(imm), 2) - (1 << 32)
        reg_values[rd] = format(pc + 4, '032b')  
        pc = int(reg_values[rs1], 2) + imm
        return pc
    if opcode_table[opcode][''][f3]=='lw':
        imm = int(sign_extension(imm), 2) if imm[0] == '0' else int(sign_extension(imm), 2) - (1 << 32)
        reg_values[rd] = int(reg_values[rs1], 2) + imm
        reg_values[rd] = format(reg_values[rd] & 0xFFFFFFFF, '032b')
        return pc + 4

def B_execute(opcode,imm,rs1,rs2,pc,f3):
    imm = int(sign_extension(imm), 2) if imm[0] == '0' else int(sign_extension(imm), 2) - (1 << 32)
        
    if opcode_table[opcode][''][f3]=='beq':
        if reg_values[rs1]==reg_values[rs2]:
            if imm==0:
                return "HALT"
            return pc+imm
        return pc+4
    if opcode_table[opcode][''][f3]=='bne':
        if reg_values[rs1]!=reg_values[rs2]:
            if imm==0:
                return "HALT"
            return pc+imm
        return pc+4
    
def run(l):
    l = [x.strip() for x in l]
    l = [x for x in l if x]
    #print(l)
    dct = {}
    for i in range(len(l)):
        dct[i*4] = l[i]
    print(dct)
    pc=0
    while pc in dct:
        line = dct[pc]
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
            pc+=4


        elif it=='I':
            imm=line[:12]
            rs1=line[12:17]
            f3=line[17:20]
            rd=line[20:25]
            assert checkI(opcode,f3)
            assert rs1 in registers
            pc=I_execute(imm, rs1 ,f3, rd,opcode,pc)

        elif it=='S':
            imm=line[:7]+line[20:25]
            rs2=line[7:12]
            rs1=line[12:17]
            f3=line[17:20]
            assert checkS(opcode,f3)
            assert rs1 in registers
            assert rs2 in registers
            pc+=4

        elif it=='B':
            imm=line[0]+line[24]+line[1:7]+line[20:24]
            rs2=line[7:12]
            rs1=line[12:17]
            f3=line[17:20]
            assert checkB(opcode,f3)
            assert rs1 in registers
            assert rs2 in registers
            pc=B_execute(opcode,imm,rs1,rs2,pc,f3)
            if pc=="HALT":
                print("HALT")
                break
        elif it=='J':
            imm = line[0] + line[12:20] + line[11] + line[1:11]
            rd=line[20:25]
            assert rd in registers
            assert checkJ(opcode)
            assert rd in registers
            pc = J_execute(opcode,imm,rd,pc)
        else:
            raise ValueError("UNKNOWN OPCODE")
        print(it)
        print(reg_values)
        print("\n"*5)


    
#inp="bin.txt"
#inp = r'C:\Users\Ashish Gupta\Desktop\co-midsem project\SimpleSimulator\bin.txt'
inp = r'C:\Users\amrit\Documents\co\co-assignment\SimpleSimulator\bin.txt'
with open(inp, "r") as f:
    l = f.readlines()
run(l)
