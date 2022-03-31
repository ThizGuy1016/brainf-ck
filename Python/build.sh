#! /usr/bin/sh

set -xe

nasm -f elf64 -g test.asm -o test.o
ld test.o -o test
./test
