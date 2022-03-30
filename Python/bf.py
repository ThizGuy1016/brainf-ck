#!/usr/bin/env python3
from enum import IntEnum, unique, auto
from collections.abc import Sequence
from pathlib import Path
import sys

STACK_MAX: int = 30000

@unique
class OPCODE(IntEnum):
    INC=auto()
    DEC=auto()
    ADD=auto()
    SUB=auto()
    BLOOP=auto()
    ELOOP=auto()
    INPUT=auto()
    OUTPUT=auto()
    BSYSCALL=auto()
    ESYSCALL=auto()
    NOOP=auto()

OPCODE_PAIR: dict[chr, OPCODE] = {
    '>': OPCODE.INC,
    '<': OPCODE.DEC,
    '+': OPCODE.ADD,
    '-': OPCODE.SUB,
    '[': OPCODE.BLOOP,
    ']': OPCODE.ELOOP,
    ',': OPCODE.INPUT,
    '.': OPCODE.OUTPUT,
    '(': OPCODE.BSYSCALL,
    ')': OPCODE.ESYSCALL,
}

assert len(OPCODE_PAIR) == len(OPCODE) - 1, "Non exhaustive handiling of opcodes while parsing."

OpAmount = int
OpcodePair = tuple[OPCODE, OpAmount] # OP_Amount can also be a 
Program = list[OpcodePair]
Stack = list[int]
StackCounter = list[int]

def parse_program(path: Path) -> str:
    with open(path, 'r') as p:
        try: return p.read()
        except Exception as e: raise Exception(f"File error: {e}")

def lex_program(program_str: str) -> list[OPCODE]:
    
    """
    Loops through symbols in program string and returns the opcode value of all valid symbols.
    """
    
    opcode_list: list[OPCODE] = []
    for symbol in program_str:
        try: opcode_list.append(OPCODE_PAIR[symbol])
        except: pass
    return opcode_list

def group_ops_recurs(opcode_list: list[OPCODE], program_buf: Program, program_counter: list[int], opcode_condition) -> None:
    """
    Allows grouping opcodes to be done recursively
    """
    
    while True:
    
        if program_counter[0] >= len(opcode_list): return 
        current_opcode = opcode_list[program_counter[0]]

        if opcode_condition(current_opcode):
            return

        if current_opcode == OPCODE.BLOOP:
            bloop_amount: Program = [(0, 0)]
            program_counter[0] += 1
            
            group_ops_recurs(opcode_list, bloop_amount, program_counter, lambda x: x == OPCODE.ELOOP)
            
            try: del opcode_list[program_counter[0]] # removes the ending delimeter
            except: assert False, "Unmatched closing delimeter for '['"
            
            #if len(bloop_amount[1:]) > 1: 
            #    bloop_amount.append((OPCODE.NOOP, 1))
            program_buf.append((OPCODE.BLOOP, tuple(bloop_amount[1:])))

        # increase opcode amount if last opcode == current_opcode
        elif program_buf[-1][0] == current_opcode:
            program_buf[-1] = (program_buf[-1][0], program_buf[-1][1] + 1)
            program_counter[0] += 1
    
        else:
            program_buf.append((current_opcode, 1))
            program_counter[0] += 1

def group_ops(opcode_list: list[OPCODE]) -> Program:
    
    """
    An optimization step to group identical opcodes into an opcode amount.
    """

    program_buf: Program = [(0, 0)]
    program_counter: list[int] = [0]
    for _ in enumerate(opcode_list):
        group_ops_recurs(opcode_list, program_buf, program_counter, lambda x: False)

    return program_buf[1:]

def compile_program(program: Program) -> None:
    assert False, "Not Implemented"

def simulate_opcode(opcode: OpcodePair, stack_counter: StackCounter, stack: Stack) -> None:
    """
    Allows the simulation of opcodes to be done recursively
    """

    match opcode[0]:
        case OPCODE.INC:
            #print(f"Incrementing: {opcode[1]}")
            stack_counter[0] += opcode[1]
        case OPCODE.DEC:
            #print(f"Decrementing: {opcode[1]}")
            stack_counter[0] -= opcode[1]
        
        case OPCODE.ADD:
            #print(f"Adding: {opcode[1]}")
            stack[stack_counter[0]] += opcode[1]
        case OPCODE.SUB: 
            #print(f"Subbing: {opcode[1]}")
            stack[stack_counter[0]] -= opcode[1]
        
        case OPCODE.BLOOP:

            while True:
                #print(f"Looping")
                for bloop_opcodes in opcode[1]:
                    simulate_opcode(bloop_opcodes, stack_counter, stack)
                if stack[stack_counter[0]] == 0: return

        case OPCODE.INPUT: 
            for _ in range(opcode[1]):
                x = input('')
                assert x.isnumeric(), "Input was Nan"
                stack[stack_counter[0]] = int(x)
        
        case OPCODE.OUTPUT: 
            for _ in range(opcode[1]):
                print(chr(stack[stack_counter[0]]),end='')
                pass

        case OPCODE.BSYSCALL: assert False, "Not Implemented"
        
        case OPCODE.NOOP: 
            for _ in range(opcode[1]):
                continue

        case _ as e: 
            assert False, f"Failed at instruction: {e}"

    return

def simulate_program(program: Program) -> None:

    stack: Stack = [0 for i in range(STACK_MAX)]
    stack_counter: StackCounter = [0]

    for opcode in program:

        if stack[stack_counter[0]] < 0: stack[stack_counter[0]] = sys.maxsize

        simulate_opcode(opcode, stack_counter, stack)

def main() -> None:
    program_path = Path('hello.bf')
    program = parse_program(program_path)
    program = lex_program(program)
    program = group_ops(program)

    simulate_program(program)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: exit(0)
