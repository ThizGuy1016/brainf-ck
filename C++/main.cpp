#include <iostream>
#include <fstream>
#include <optional>
#include <string>

#include "parser.hpp"
#include "unwrap.hpp"

using namespace Unwrap;

auto main() -> int
{

	Tokenizer t(">>>>", std::vector<Tokenizer::Directive_t>{Directive_group_ops});
	ProgramBody_t program = Program_from(t);

	for ( const OpcodePair_t& pair : program )
		std::cout << pair << std::endl;

	return 0;
}
