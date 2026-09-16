lexer grammar SuaLing;

// Produzidos pela etapa de layout em src/analise_lexica.py.
tokens { NOVA_LINHA, INDENTA, DEDENTA }

// Palavras reservadas: antes de IDENT para desempatar lexemas iguais.
TIPO_INTEIRO : 'inteiro';
TIPO_REAL    : 'real';
TIPO_TEXTO   : 'texto';
TIPO_BOOLEANO: 'booleano';
VERDADEIRO   : 'verdadeiro';
FALSO        : 'falso';
CONCLUIR     : 'concluir';
QUANDO       : 'quando';
ENCERRAR     : 'encerrar';
OPERACAO     : 'operacao';
REQUER       : 'requer';
INICIAR      : 'iniciar';
COM          : 'com';
NARRAR       : 'narrar';
SE           : 'se';
SENAO        : 'senao';
E            : 'e';
OU           : 'ou';
NAO          : 'nao';

IGUAL        : '==';
DIFERENTE    : '!=';
MENOR_IGUAL  : '<=';
MAIOR_IGUAL  : '>=';
ATRIBUICAO   : '=';
MENOR        : '<';
MAIOR        : '>';
MAIS         : '+';
MENOS        : '-';
MULTIPLICACAO: '*';
DIVISAO      : '/';
PONTO        : '.';
ABRE_PAREN   : '(';
FECHA_PAREN  : ')';
VIRGULA      : ',';

REAL         : [0-9]+ '.' [0-9]+;
INTEIRO      : [0-9]+;

// O maior casamento captura 12abc, 1e3, 3., .5 e 1.2.3 inteiros.
// Em empate, as regras REAL/INTEIRO acima vencem para numeros validos.
NUMERO_MALFORMADO
    : [0-9]+ [a-zA-Z_0-9.]*
    | '.' [0-9]+ [a-zA-Z_0-9.]*
    ;

TEXTO
    : '"' ('\\' ["\\nt] | ~["\\\r\n])* '"'
    ;

// Captura texto com escape invalido ou sem fechamento, sem engolir a linha seguinte.
// TEXTO vem antes e vence o empate para literais validos.
TEXTO_INVALIDO
    : '"' ('\\' ~[\r\n] | ~["\\\r\n])* ('"' | '\\'?)
    ;

IDENT        : [a-zA-Z_] [a-zA-Z_0-9]*;
COMENTARIO   : '//' ~[\r\n]* -> skip;
ESPACO       : [ \r\n]+ -> skip;

// Tokens de erro sao diagnosticados pelo programa, nunca listados como validos.
TABULACAO    : '\t';
CARACTERE_INVALIDO : .;
