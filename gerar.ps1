$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & antlr4 -v 4.13.2 -Dlanguage=Python3 -Xexact-output-dir -o gerado gramatica/SuaLing.g4
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar o lexer ANTLR (codigo $LASTEXITCODE)."
    }
} finally {
    Pop-Location
}
