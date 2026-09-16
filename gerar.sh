#!/usr/bin/env sh
set -eu
cd -- "$(dirname -- "$0")"
antlr4 -v 4.13.2 -Dlanguage=Python3 -Xexact-output-dir -o gerado gramatica/SuaLing.g4
