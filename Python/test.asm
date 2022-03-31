section .data

	SYS_WRITE: equ 1
	SYS_OUT: equ 1 

	STACK_MAX: equ 30000

	message: db "Hello World",0xA
	message_len: equ $-message

section .bss
	digit_space: resb 8
	stack: resq STACK_MAX 

section .text
global _start

_clear_loop:
	mov QWORD stack[r8d], 0
	inc r8d
	cmp r8d, STACK_MAX
	jle _clear_loop
	mov r8d, 0
	ret

%macro outputOP 1:
	push %1
	mov rax, 1
	mov rdi, SYS_OUT
	mov rsi, rsp
	mov rdx, 8 
	syscall
	pop rcx
%endmacro

_inputOP:
	ret


_start:

	mov r8d, 0
	call _clear_loop

	mov QWORD stack[r8d], 33
	add r8d, 1
	dec r8d
	mov rax, stack[r8d]

	outputOP rax

	outputOP 10

	mov rax, 60
	mov rdi, 0
	syscall
