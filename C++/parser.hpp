#pragma once

#include <unordered_map>
#include <functional>
#include <optional>
#include <vector>
#include <string>

#include "unwrap.hpp"

using Token_t = char;
using Opcode_t = uint16_t;

enum struct Opcode : Opcode_t {
	Inc,
	Dec,
	Add,
	Sub,
	Out,
	Inp,
	BLoop,
	ELoop,
	NoOp,
};

using OpcodeDict_t = typename std::unordered_map<Token_t, Opcode>;
OpcodeDict_t OpcodeDict = {
	{'>', Opcode::Inc  },
	{'<', Opcode::Dec  },
	{'+', Opcode::Add  },
	{'-', Opcode::Sub  },
	{'.', Opcode::Out  },
	{',', Opcode::Inp  },
	{'[', Opcode::BLoop},
	{']', Opcode::ELoop},
};

using OpcodePair_t = typename std::tuple<Opcode, uint64_t>;

auto OpcodePair_from(const Token_t& t, const uint64_t op_amount=1) -> const std::optional<OpcodePair_t>
{
	for ( const auto& [k, v] : OpcodeDict ) 
		if (t == k) 
			return std::make_tuple(v, op_amount);
	return std::nullopt;
}

auto OpcodePair_to(const OpcodePair_t& op_pair) -> const std::optional<char>
{
	for ( const auto& [k, v] : OpcodeDict )
		if (std::get<0>(op_pair) == v)
			return k;
	return std::nullopt;
}

using ProgramBody_t = typename std::vector<OpcodePair_t>;

struct Tokenizer {

	using Directive_t = typename std::function<void(Tokenizer&)>;	

	const std::string				program;
	size_t							program_counter;
	std::optional<OpcodePair_t>		program_look_ahead;
	ProgramBody_t					program_body;
	std::vector<Directive_t>		program_directives;

	Tokenizer(const std::string _program)
	: program(std::move(_program)), program_counter(0), program_look_ahead(next())
	{
	}

	Tokenizer(const std::string _program, const std::vector<Directive_t>& _program_diretives)
	: program(std::move(_program)), program_counter(0), program_look_ahead(next()), program_directives(_program_diretives)
	{
	}

	/*
	 | Checks if program has remaining tokens
	*/
	auto has_remaining_toks() -> const bool 
	{
		return (program_counter < program.size()) ? true : false;
	}

	/*
	 | Gets the next token in the program
	*/
	auto next() -> const std::optional<OpcodePair_t>
	{
		if (!has_remaining_toks())
			return std::nullopt;
		return OpcodePair_from(program[program_counter++]);
	}

	/*
	 | Returns the next opcode if it matches the provided opcode
	*/
	auto consume(const Opcode& op) -> const std::optional<OpcodePair_t>
	{
		if (!program_look_ahead || std::get<0>(*program_look_ahead) != op)
			return std::nullopt;
		program_look_ahead = next();
		return *program_look_ahead;
	}

	auto apply_directives() -> void
	{
		for ( auto& directive : program_directives )
			directive(*this);
	}
};


auto Directive_process_loop(Tokenizer& t) -> void
{

	/*
	 | This directive will iterate over program_body searching for the matching Opcode::ELoop pair.
	 | Opcode::Bloop as well as the program_idx of the matching Opcode::ELoop will be stored. 
	 | To account for nested loops, bloop_counter will increment by 1 everytime Opcode::Bloop is encountered.
	 | bloop_counter will also decrement by 1 everytime Opcode::ELoop is encountered.
	 | bloop_counter must be zero to store the matching Opcode::Eloop idx.
	*/

	ProgramBody_t program_buf;
	for ( size_t program_idx = 0; program_idx < t.program_body.size(); ++program_idx ) {
		
	}
	t.program_body = program_buf;
}

auto Directive_group_ops(Tokenizer& t) -> void 
{
	ProgramBody_t program_buf;
	program_buf.reserve(t.program_body.size());

	Opcode curr_op;
	uint64_t curr_op_amount = 1;
	size_t bloop_counter = 0;
	for ( size_t program_idx = 0; program_idx < program_buf.size(); ++program_idx ) {
		curr_op = std::get<0>(t.program_body[program_idx]);

		switch (curr_op) {
			case Opcode::Inc:
				while ( t.consume(Opcode::Inc) )
					++curr_op_amount;
				
				program_buf.emplace_back(std::make_tuple(Opcode::Inc, curr_op_amount));
				curr_op_amount = 1;
				
				break;
			case Opcode::Dec:
				while( t.consume(Opcode::Dec) )
					++curr_op_amount;
				
				program_buf.emplace_back(std::make_tuple(Opcode::Dec, curr_op_amount));
				curr_op_amount = 1;
				
				break;
			case Opcode::Add:
				while ( t.consume(Opcode::Add) )
					++curr_op_amount;

				program_buf.emplace_back(std::make_tuple(Opcode::Add, curr_op_amount));
				curr_op_amount = 1;

				break;
			case Opcode::Sub:
				while ( t.consume(Opcode::Sub) )
					++curr_op_amount;

				program_buf.emplace_back(std::make_tuple(Opcode::Add, curr_op_amount));
				curr_op_amount = 1;

				break;
			/*
			 | Unlikely that the program_buf opcodes will be initialized by anything but 1
			 | but I mean safety 1st
			*/
			case Opcode::Out:
				program_buf.emplace_back(std::make_tuple(Opcode::Out, 1));

				break;
			case Opcode::Inp:
				program_buf.emplace_back(std::make_tuple(Opcode::Inp, 1));

				break;
			case Opcode::BLoop:
				program_buf.emplace_back(std::make_tuple(Opcode::BLoop, 1));
				break;
			case Opcode::ELoop:
				program_buf.emplace_back(std::make_tuple(Opcode::ELoop, 1));
				break;
			case Opcode::NoOp:
				break;
		}

	}

	program_buf.shrink_to_fit();

	t.program_body = program_buf;
}

auto Program_from(Tokenizer& t, const std::vector<Tokenizer::Directive_t>& directives=std::vector<Tokenizer::Directive_t>{ [](Tokenizer&) { return; } }) -> ProgramBody_t
{	
	/*
	 | If the program is empty
	*/
	if (!t.program_look_ahead)
		return ProgramBody_t {std::make_tuple(Opcode::NoOp, 1)};
	
	/*
	 | Since the program body can only be as large as the t.program.size(),
	 | the program body reserves t.program.size() bytes 
	*/
	ProgramBody_t program_body;
	program_body.reserve(t.program.size());
	program_body.emplace_back(std::make_tuple(*t.program_look_ahead, 1));
	
	while ( t.has_remaining_toks() ) {
		const std::optional<OpcodePair_t> next_op = t.next();
		if (!next_op)
			continue;
		program_body.emplace_back(std::make_tuple(*next_op, 1));
	}

	/*
	 | Because bf treats all non-opcode characters as comments we shrink the program_body
	 | such that it only contains valid opcodes
	*/	
	program_body.shrink_to_fit();
	
	return program_body;
}

auto Program_from(Tokenizer& t, const Tokenizer::Directive_t& directive) -> ProgramBody_t
{
	return Program_from(t, std::vector<Tokenizer::Directive_t>{directive});
}

auto Program_slice(const ProgramBody_t& program_body, size_t start, size_t end)
{
	const auto first = program_body.cbegin() + start;
	const auto last = program_body.cbegin() + end + 1;

	return ProgramBody_t(first, last); 

}

auto operator<<(std::ostream& os, const OpcodePair_t& op_pair) -> std::ostream&
{
	return os << '(' << static_cast<Opcode_t>(std::get<0>(op_pair)) << ',' << std::get<1>(op_pair) << ')';
}
