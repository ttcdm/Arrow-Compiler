# Arrow-Compiler
Compiler for the Arrow programming language into 6502 assembly

Arrow files are stored as .aro
The python script compiles and outputs the 6502 assembly into 6asm.txt

Arrow supports integer addition, subtraction, multiplication, and division.
It also supports variables, arrays, conditional statements, for loops, and nesting,
but there's a limit to nesting because the jump range of 6502 assembly is limited to around 128 bytes.
There isn't really a type system. The main type is an integer, but since it's so primitive,
everything's just stored as an integer variable or an array. There is no support for pointers.
