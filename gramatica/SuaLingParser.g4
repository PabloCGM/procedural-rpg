parser grammar SuaLingParser;

options {
    tokenVocab = SuaLing;
}

// Regra raiz inicial mínima da E3
programa
    : EOF
    ;

