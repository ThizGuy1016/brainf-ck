#! /bin/sh

set -xe

clang-tidy -checks=modernize* -header-filter=.* main.c -- | less
clang -std=c11 -stdlib=libc -Wall -pedantic main.c -o bf.out
