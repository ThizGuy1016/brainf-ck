#! /bin/env python3.10

from typing import AnyStr, Mapping, Generator, Callable
from collections.abc import Sequence
from enum import Enum, unique, auto
from pathlib import Path
import sys

class OPCODE(Enum):
    INC=auto()
    DEC=auto()
    ADD=auto()
    SUB=auto()
    BLOOP=auto()
    ELOOP=auto()
    NO_OP=auto()

OPCODE_DICT: Mapping[str, OPCODE] = {
    '>': OPCODE.INC,
    '<': OPCODE.DEC,
    '+': OPCODE.ADD,
    '-': OPCODE.SUB,
    '[': OPCODE.BLOOP,
    ']': OPCODE.ELOOP
}

assert len(OPCODE_DICT) == len(OPCODE) - 1, "Non-exhaustive handling of opcodes while parsing."

OpAmount = int
OpcodePair = tuple[OPCODE, OpAmount]
Program = list[tuple[Path, int, int, OpcodePair]]
ProgramMem = list[int]
ProgramCounter = list[int]

def lex_word(line: str, opcode_dict: Mapping[str, OPCODE], delim: str = ' ') -> Generator[tuple[int, OPCODE], None, None]:
    col: int = 0
    for tok in line.replace('\n', '').split(delim):
        if tok in opcode_dict:
            col += 1
            yield (col, opcode_dict[tok])

def lex_char(line: str, opcode_dict: Mapping[str, OPCODE], delim: str = ' ') -> Generator[tuple[int, OPCODE], None, None]:
    for col, tok in enumerate(line):
        if tok in opcode_dict:
            yield (col, opcode_dict[tok])

# thank you zozek
def lex_file(file: Path, opcode_dict: Mapping[str, OPCODE], delim: str = ' ') -> Program: 
    expr: Callable[[str, Mapping[str, OPCODE], str], Generator[tuple[int, OPCODE], None, None]] = lex_char 
    
    for key in opcode_dict:
        if len(key) > 1:
            expr = lex_word
            break
    
    with open(file, 'r') as p:
        return [(file, row, col, (tok, 1)) for (row, line) in enumerate(p.readlines())
                                           for (col, tok) in expr(line, opcode_dict, delim)]

def process_loop(program: Program) -> None:
    """
    Iterates over a program and gives each loop OPCODE an index to the end loop
    """
    idx: int = 0
    while idx < len(program):
               
        if program[idx][3][0] is OPCODE.BLOOP:
 
            bloop_counter: int = idx + 1
            if bloop_counter == len(program): return 
            
            recurse_counter: int = 0
 
            while program[idx][3][0] is not OPCODE.ELOOP and recurse_counter == 0:

                bloop_opcode: OPCODE = program[idx][3][0]
                
                if bloop_counter == len(program): raise Exception("Unmatched in bloop loop")
                elif bloop_opcode is OPCODE.BLOOP:
                    recurse_counter += 1
                elif bloop_opcode is OPCODE.ELOOP: 
                    recurse_counter -= 1
                idx += 1

            curr: tuple[Path, int, int, OpcodePair] = program[bloop_counter]
            program[bloop_counter] = (curr[0], curr[1], curr[2], (OPCODE.BLOOP, idx))
        
        
            idx = bloop_counter 

def preprocessor(program_opcodes: Program, directives: list[Callable[[Program], None]]) -> Program:
    for directive in directives:
        directive(program_opcodes)
    return program_opcodes

def main() -> None:
    lexed = lex_file(Path("test.bf"), OPCODE_DICT)
    #[print(i) for i in lexed]
    program = preprocessor(lexed, [process_loop])
    [print(i) for i in program]

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
