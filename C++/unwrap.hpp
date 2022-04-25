#pragma once

#include<iostream>
#include<optional>
#include<cassert>

namespace Unwrap
{

	template<typename OPT_t>
	auto unwrap_assert(const std::optional<OPT_t>& opt) -> OPT_t;
	
	template<typename OPT_t>
	auto unwrap_or(const std::optional<OPT_t>& opt, const char* err_msg, std::ostream& err_os=std::cerr, void(*err_fun)() = [](){return;}, const int& err_code=1) -> OPT_t;

	template<typename OPT_t>
	auto unwrap_or_else(const std::optional<OPT_t>& opt, const OPT_t& val) -> OPT_t;

}

template<typename OPT_t>
auto Unwrap::unwrap_assert(const std::optional<OPT_t>& opt) -> OPT_t
{
	assert(opt.has_value());
	return *opt;
}

template<typename OPT_t>
auto Unwrap::unwrap_or(const std::optional<OPT_t>& opt, const char* err_msg, std::ostream& err_os, void(*err_fun)(), const int& err_code) -> OPT_t
{
	if (!opt) {
		err_os << err_msg;
		atexit(err_fun);
		exit(err_code);
	}
	return *opt;
}

template<typename OPT_t>
auto Unwrap::unwrap_or_else(const std::optional<OPT_t>& opt, const OPT_t& val) -> OPT_t
{
	if (!opt)
		return val;
	return *opt;
}

