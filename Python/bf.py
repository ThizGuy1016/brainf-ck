#!/usr/bin/env python3
from enum import IntEnum, unique, auto
from collections.abc import Sequence
from pathlib import Path
from typing import Any 
import argparse
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

OPCODE_PAIR: dict[str, OPCODE] = {
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
OpcodePair = tuple[OPCODE, Any] # OP_Amount can be int or tuples of other opcodes 
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
            bloop_amount: Program = [(OPCODE.NOOP, 0)]
            program_counter[0] += 1
            
            group_ops_recurs(opcode_list, bloop_amount, program_counter, lambda x: x == OPCODE.ELOOP)
            
            try: del opcode_list[program_counter[0]] # removes the ending delimeter
            except: assert False, "Unmatched closing delimeter for '['"
            
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

    program_buf: Program = [(OPCODE.NOOP, 0)]
    program_counter: list[int] = [0]
    for _ in enumerate(opcode_list):
        group_ops_recurs(opcode_list, program_buf, program_counter, lambda x: False)

    return program_buf[1:]

def compile_program(program: Program, output_path: Path) -> None:
    assert False, "Not Implemented"
    
    program_buf: str = ""
    loop_counter: list[int] = [0]
    for opcode in program:
        match current_opcode[0]:
            case OPCODE.INC: 
                program_buf.append(f"\tadd r8d {opcode[1]}\n")
            case OPCODE.DEC:
                probram_buf.append(f"\tsub r8d {opcode[1]}\n")
            case OPCODE.ADD:
                program_buf.append(f"\tadd stack[r8d], {opcode[1]}\n")
            case OPCODE.SUB:
                program_buf.append(f"\tsub stack[r8d], {opcode[1]}\n")
            case OPCODE.BLOOP:
                loop_counter[0] += 1
                program_buf.append(f"_wloop{loop_counter[0]}:\n")
                #compile_opcode(opcode[1], program_buf, loop_counter)
                program_buf.append(f"\tcmp stack[r8d], 0\n")
                program_buf.append(f"\tjne _wloop{loop_counter[0]}\n")
            case OPCODE.OUTPUT:
                for _ in opcode[1]:
                    program_buf.append(f"\t_outputOP stack[r8d]\n")
            case OPCODE.INPUT:
                assert False, "Not Implemented"
            case OPCODE.BSYSCALL:
                assert False, "Not Implemented"
            case OPCODE.ESYSCALL:
                assert False, "Not Implemented"

            case _:
                assert False, "WTF??"

    #with open(output_path: Path) as p:
        #try: p.write(program_buf)
        #except Exception as e: raise Exception(f"File Error: {e}")

def simulate_opcode(opcode: OpcodePair, stack_counter: StackCounter, stack: Stack) -> None:
    """
    Allows the simulation of opcodes to be done recursively
    """

    match opcode[0]:

        case OPCODE.INC: stack_counter[0] += opcode[1]
        case OPCODE.DEC: stack_counter[0] -= opcode[1]
        
        case OPCODE.ADD: stack[stack_counter[0]] += opcode[1]
        case OPCODE.SUB: stack[stack_counter[0]] -= opcode[1]
        
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

        case OPCODE.BSYSCALL: assert False, "Syscalls are not yet Implemented"
        case OPCODE.ESYSCALL: assert False, "Syscalls are not yet Implemented"
        
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

def parse_args() -> tuple[Path, bool, bool, bool]:

    parser = argparse.ArgumentParser(description="Brainfuck interpereter and compiler")
    parser.add_argument("run_type", type=str, nargs='?', help="Option to compile 'com', or simulate 'sim', the Brainfuck program")
    parser.add_argument("path", type=str, nargs='?', help="Path to the Brainfuck program")
    parser.add_argument("-v", "--verbose", action="store_true", required=False, help="Sets the verbosity level of the program")
    try: args = parser.parse_args()
    except argparse.ArgumentError as e: raise argparse.ArgumentError(None, message = f"Command-Line args Error: {e}")

    simu: bool = False
    comp: bool = False
    verbose: bool = False

    if args.verbose: verbose = True

    if args.run_type == "sim": simu = True
    elif args.run_type == "com": comp = True
    else: raise Exception("Invalid run-type provided.")

    return (Path(args.path), simu, comp, verbose)

def main() -> None:

    program_path, simu, comp, verbose = parse_args()

    # I'll make this more functional later
    program: Program = group_ops(lex_program(parse_program(program_path)))

    if simu: 
        if verbose:
            print(f"[INFO] Simulating program: {program_path}")
        simulate_program(program)
    if comp: 
        if verbose:
            print(f"[INFO] Compiling program: {program_path}")
        compile_program(program)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: exit(0)
    except Exception as e: 
        print(f"[ERROR]: {e}")
        exit()
