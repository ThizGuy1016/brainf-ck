#! /bin/sh

set -xe

clang-tidy -checks=modernize* -header-filter=.* main.cpp -- -std=c++17 | less
clang++ -std=c++17 -stdlib=libc++ -Wall -pedantic main.cpp -o bf.out

