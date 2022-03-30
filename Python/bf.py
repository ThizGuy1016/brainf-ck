#!/usr/bin/env python3

from pathlib import Path
import argparse
import sys

iota_counter = 0
def iota(reset: bool = False) -> int:
    global iota_counter
    if reset: iota_counter = 0
    iota_counter += 1
    return iota_counter

OP_INC=iota(True)   # 1 >
OP_DEC=iota()       # 2 <
OP_ADD=iota()       # 3 +
OP_SUB=iota()       # 4 -
OP_BLOOP=iota()     # 5 [
OP_ELOOP=iota()     # 6 ]
OP_INPUT=iota()     # 7 ,
OP_OUTPUT=iota()    # 8 .
OP_BSYSCALL=iota()  # 9 (
OP_ESYSCALL=iota()  # 10 )
COUNT_OPS=iota()    # 11

def compile_program(program: list) -> None:
    assert False, "Not Implemented"

def group_loop(program_counter: int, program: list[int], ops: list[int, int]) -> None:
    current_opcode: int = program[program_counter]
    while_counter: int = program_counter
    while current_opcode != OP_ELOOP:
        assert while_counter < len(program) - 1, "Unmatched closing delimeter for '['" 
        while_counter += 1
        if program[while_counter] == OP_BLOOP:
            group_loop(while_counter, program, ops)
        current_opcode = program[while_counter]
    del program[while_counter] # removes the ending loop opcode
    del program[program_counter]
    ops.append((OP_BLOOP, while_counter - 2)) # used to align the ending range of the loop with the starting range, change this is shit dont work

def group_ops(program: list[int]) -> list[int]:
    ops: list[int, int] = [(0, 0)] # (opcode, amount) / (opcode, closing delimeter)
    program_counter: int = 0
    for _ in enumerate(program):
        if program_counter >= len(program):
            continue
        current_opcode: int = program[program_counter]
        
        # if we have a begining loop operation
        if current_opcode == OP_BLOOP:
            group_loop(program_counter, program, ops)

        # the current instruction opcode is an endloop
        elif current_opcode == OP_ELOOP: 
            ops.append((OP_ELOOP, 1))

        # if the last instruction opcode is the same as the current instruction opcode
        elif ops[-1][0] == current_opcode:
            ops[-1] = (ops[-1][0], ops[-1][1] + 1)

        else:
            ops.append((program[program_counter], 1))

        program_counter += 1

    return ops[1:]

def simulate_program(program: list[int]) -> None:
    STACK_MIN: int = 0
    STACK_MAX: int = 1000

    stack: list[int] = [0 for i in range(STACK_MIN,STACK_MAX)]    
    stack_counter: int = 0
    _ = simulate_opcodes(0, len(program) - 1, program, stack, stack_counter)

def simulate_opcodes(program_counter: int, end_idx: int, program: list[int], stack: list[int], stack_counter: int) -> [int, int]:
    while program_counter <= end_idx:

        if stack_counter < 0: stack_counter = sys.maxsize
        if stack[stack_counter] < 0: stack[stack_counter] = sys.maxsize

        opcode: int = program[program_counter][0]
        amount: int = program[program_counter][1]

        if opcode == OP_INC:
            stack_counter += amount

        elif opcode == OP_DEC: 
            stack_counter -= amount

        elif opcode == OP_ADD: 
            stack[stack_counter] += amount
        
        elif opcode == OP_SUB: 
            stack[stack_counter] -= amount

        elif opcode == OP_BLOOP:
            while True:
                loop_begin: int = program_counter
                # this is inefficient... but I refuse to write a class
                assert amount <= end_idx, "Loops bounds exceded program size"
                stack, stack_counter = simulate_opcodes(loop_begin + 1, amount, program, stack, stack_counter)
                loop_begin = program_counter
                if stack[stack_counter] == 0: 
                    program_counter += 1
                    break

        elif opcode == OP_OUTPUT: 
            for _ in range(amount):
                print((stack[stack_counter]))
        elif opcode == OP_INPUT: 
            for _ in range(amount):
                x = input('')
                assert x.isnumeric(), "Input was Nan"
                stack[stack_counter] = int(x)

        elif opcode == OP_BSYSCALL: assert False, "Not implemented"
        elif opcode == OP_ESYSCALL: assert False, "Not implemented"

        else: assert False, "Unknown opcode encountered during simulation"

        program_counter += 1

    return stack, stack_counter

def lex_program(contents: str) -> list[int]:
    opcodes: dict = { '>': OP_INC, '<': OP_DEC, '+': OP_ADD, '-': OP_SUB, '[': OP_BLOOP, ']': OP_ELOOP, '(': OP_BSYSCALL, ')': OP_ESYSCALL }
    return [opcodes[i] for i in contents if i in opcodes]

def read_program(path: Path) -> str:
    with open(path, "r") as p:
        try: return p.read()
        except Exception as e: raise Exception(f"File error: Failed to read program file: {path}\n{e}")

def main() -> None:
    #program_path: Path = Path("hello.bf")
    #contents = read_program(program_path)
    #lexed_program = lex_program(contents)
    #grouped = group_ops(lexed_program)
    
    grouped = group_ops([
        OP_INC,
        OP_ADD,
        OP_INC,
        OP_ADD,
        OP_BLOOP,
        OP_DEC,
        OP_BLOOP,
        OP_SUB,
        OP_ELOOP,
        OP_ELOOP,
        ])

    print(grouped)
    print(len(grouped))

    simulate_program(grouped)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: exit(0)
