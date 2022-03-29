#!/usr/bin/env python3
from pathlib import Path
import argparse

iota_counter = 0
def iota(reset: bool = False) -> int:
    global iota_counter
    if reset: iota_counter = 0
    iota_counter += 1
    return iota_counter

OP_INC=iota(True)   # 1 >
OP_DEC=iota()       # 2 <
OP_PLUS=iota()      # 3 +
OP_MINUS=iota()     # 4 -
OP_BLOOP=iota()     # 5 [
OP_ELOOP=iota()     # 6 ]
OP_INPUT=iota()     # 7 ,
OP_OUTPUT=iota()    # 8 .
OP_BSYSCALL=iota()   # 9 (
OP_ESYSCALL=iota()  # 10 )
COUNT_OPS=iota()    # 11

STACK_MIN: int = 0
STACK_MAX: int = 1000

stack: list[int] = [i for i in range(STACK_MIN,STACK_MAX)]    
counter: int = 0

def compile_program(program: list) -> None:
    assert False, "Not Implemented"

def group_ops(program: list[int]) -> list[int]:
    ops: list[int, int] = [(0, 0)] # (opcode, amount)
    for op in program:
        last_op = ops[-1]
        if op == last_op[0]:
            ops[-1] = (op, last_op[1] + 1)
            continue
        ops.append((op, 1))
    return ops[1:]

def match_ops(op: list) -> None:
    global counter, stack

    opcode = op[1][0]
    amount = op[1][1]
    idx = op[0]
    if opcode == OP_INC: counter += amount
    elif opcode == OP_DEC: counter -= amount
    elif opcode == OP_PLUS: stack[counter] += amount
    elif opcode == OP_MINUS: stack[counter] += amount
    elif opcode == OP_BLOOP:
        bloop_idx: int = idx
        eloop_idx: int = idx
        while program[eloop_idx][1][0] != OP_ELOOP:
           eloop_idx += 1 

        


    elif opcode == OP_ELOOP: pass
    elif opcode == OP_OUTPUT: print(chr(stack[counter]))
    elif opcode == OP_INPUT: 
        x = input("")
        assert x.isnumeric(), "Input was NAN"
        stack[counter] = x
    elif opcode == OP_BSYSCALL: assert False, "Not Implemented"
    elif opcode == OP_ESYSCALL: assert False, "Not Implemented"
    else: assert False, "WTF??"

def simulate_program(program: list[int, int]) -> None: 
    for op in enumerate(program):
        match_ops(program) 

def lex_program(contents: str) -> list[int]:
    opcodes: dict = { '>': OP_INC, '<': OP_DEC, '+': OP_PLUS, '-': OP_MINUS, '[': OP_BLOOP, ']': OP_ELOOP, '(': OP_BSYSCALL, ')': OP_ESYSCALL }
    return [opcodes[i] for i in contents if i in opcodes]

def read_program(path: Path) -> str:
    with open(path, "r") as p:
        try: return p.read()
        except Exception as e: raise Exception("File error: Failed to read program file: {path}\n{e}")

def main() -> None:
    program_path: Path = Path("hello.bf")
    contents = read_program(program_path)
    lexed_program = lex_program(contents)
    simulate_program(group_ops(lexed_program)) 

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: exit(0)
