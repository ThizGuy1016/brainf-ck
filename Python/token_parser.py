#! /bin/env python3.10

from typing import AnyStr, Mapping, Generator, Callable
from enum import Enum, unique, auto
from collections.abc import Sequence
from pathlib import Path
import sys

class OPCODE(Enum):
    INC=auto()
    DEC=auto()
    ADD=auto()
    SUB=auto()
    BLOOP=auto()
    ELOOP=auto()
    NOOP=auto()

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
LexedOpcodes = list[tuple[Path, int, int, OPCODE]]
OpcodePair = tuple[OPCODE, int]
GroupedOpcodes = list[tuple[Path, int, int, OpcodePair]]
Program = list[OpcodePair]
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
def lex_file(file: Path, opcode_dict: Mapping[str, OPCODE], delim: str = ' ') -> LexedOpcodes: 
    expr: Callable[[str, Mapping[str, OPCODE], str], Generator[tuple[int, OPCODE], None, None]] = lex_char 
    
    for key in opcode_dict:
        if len(key) > 1:
            expr = lex_word
            break
    
    with open(file, 'r') as p:
        return [(file, row, col, tok) for (row, line) in enumerate(p.readlines())
                                      for (col, tok) in expr(line, opcode_dict, delim)]

def process_loop(program: Program) -> Program:
    while idx <= len(program_opcodes):
        if idx >= len(program_opcodes): return grouped_buf[1:]
        
        current_opcode = program_opcodes[idx][3]
        
        # handles while loops
        if current_opcode is OPCODE.BLOOP:
            recurse_counter: int = 0
            bloop_idx: int = idx
            idx += 1
            if idx == len(program_opcodes):
                report = program_opcodes[idx]
                raise Exception(f"Error in '{report[0]}': ({report[1]}, {report[2]})\nUnmatched closing delimeter for '['!")
            elif program_opcodes[idx][3] is OPCODE.BLOOP: 
                recurse_counter += 1
            elif program_opcodes[idx][3] is OPCODE.ELOOP:
                report = program_opcodes[idx]
                raise Exception(f"Error in '{report[0]}': ({report[1]}, {report[2]})\nEmpty loops are not allowed!")
            while program_opcodes[idx][3] is not OPCODE.ELOOP and recurse_counter == 0:
                if idx == len(program_opcodes):
                    report = program_opcodes[idx]
                    raise Exception(f"Error in '{report[0]}': ({report[1]}, {report[2]})\nUnmatched closing delimeter for '['!")
                elif program_opcodes[idx][3] is OPCODE.BLOOP: 
                    recurse_counter += 1
                elif program_opcodes[idx][3] is OPCODE.ELOOP: 
                    recurse_counter -= 1
                idx += 1

            grouped_buf.append((OPCODE.BLOOP, (idx - 1)))
            idx = bloop_idx + 1

def group_ops(program_opcodes: LexedOpcodes) -> GroupedOpcodes:
    grouped_buf: list[OpcodePair] = [(program_opcodes[0][0], 0, 0, (OPCODE.NOOP, 0))]
    idx: int = 0

    while idx < len(program_opcodes):
        
        current_opcode = program_opcodes[idx][3]

        # ignores ending of while loop
        if current_opcode is OPCODE.BLOOP:
            grouped_buf.append((program_opcodes[idx][0], program_opcodes[idx][1], program_opcodes[idx][2], ((current_opcode, 1)))

        elif current_opcode is OPCODE.ELOOP:
            grouped_buf.append((current_opcode, 1))

        # groups last opcodes together by amount
        elif current_opcode is grouped_buf[-1][0]:
            grouped_buf[-1] = (current_opcode, grouped_buf[-1][1] + 1)
            idx += 1

        else:
            grouped_buf.append((current_opcode, 1))
            idx += 1

    return grouped_buf[1:]

def main() -> None:
    lexed = lex_file(Path("test.bf"), OPCODE_DICT)
    #[print(i) for i in lexed]
    grouped = group_ops(lexed)
    [print(i) for i in grouped]

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)
