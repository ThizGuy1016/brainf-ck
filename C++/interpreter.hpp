#pragma oncie

#include<iostream>
#include <array>

#include "parser.hpp"

constexpr uint64_t ProgramSize = 30000;

using Program = typename std::array<size_t, ProgramSize>;

struct Interpreter {
	ProgramBody_t& program_body;
	Program		   program;
	size_t		   p_idx;
	Opcode		   op;
	uint64_t	   op_amount;

	Interpreter(ProgramBody_t& _program_body) -> void
	: program_body(_program_body), p_idx(0), op(Opcode::NoOp), op_amount(0)
	{
		program.fill(0);
	}

	auto interpret(const ProgramBody_t& program_body, const size_t& start_idx, const size_t& end_idx) -> void
	{
		p_idx = start_idx;
		while ( p_idx < end_idx ) {
			op = std::get<0>(program_body[p_idx]);
			op_amount = std::get<1>(program_body[p_idx]);

			/*
			 | In case you somehow overflow the program counter...
			*/
			if (p_idx > program.size())
				p_idx = 0;
	
			switch (op) {
				case Opcode::Inc: 
					p_idx += op_amount;
					break;
				case Opcode::Dec: 
					p_idx -= op_amount;
					break;
				case Opcode::Add: 
					program[p_idx] += op_amount;
					break;
				case Opcode::Sub: 
					program[p_idx] -= op_amount;
					break;
				case Opcode::Out:
					std::cout << static_cast<char>(program[p_idx]);
					break;
				case Opcode::Inp: 
					program[p_idx] = static_cast<size_t>(std::cin.get());
					break;
				case Opcode::BLoop:
					/*
					 | Because loops can be 2-dimensional, we recursively interpret the program_body
					 | slice that the loop opcode contains until program[p_idx] = 0
					*/
					size_t loop_idx = p_idx;
					do { 
						interpret(program_body, loop_idx, op_amount);
					} while (program[p_idx] != 0);

					p_idx = loop_idx;
					break;
				case Opcode::ELoop: 
					continue;
					break;
				case Opcode::NoOp: 
					continue;
					break;
				default: 
					std::cerr << "[ERROR] Unknown Opcode passed to interpreter!\n";
					return;
			}
		}	
	}

}; // End Interpreter
