parser grammar SuaLingParser;

options {
    tokenVocab = SuaLing;
}

// Regra raiz para validação da gramática
programa
    : expr EOF
    ;

// ====================================================
// REGRA DE EXPRESSÕES (8 NÍVEIS DE PRECEDÊNCIA)
// ====================================================
expr
    // Nível 1: Chamada de função/método e acesso a membro (maior precedência)
    : expr ABRE_PAREN lista_argumentos? FECHA_PAREN       # ExprChamada
    | expr PONTO IDENT                                     # ExprAcessoMembro

    // Nível 2: Sinais unários (+ e -)
    | (MAIS | MENOS) expr                                  # ExprUnaria

    // Nível 3: Multiplicação e Divisão
    | expr (MULTIPLICACAO | DIVISAO) expr                  # ExprMultiplicativa

    // Nível 4: Adição, Subtração e Concatenação de texto
    | expr (MAIS | MENOS) expr                             # ExprAditiva

    // Nível 5: Comparações relacionais e igualdade
    | expr op_relacional expr                              # ExprRelacional

    // Nível 6: Negação lógica (nao)
    | NAO expr                                             # ExprNao

    // Nível 7: Conjunção lógica (e)
    | expr E expr                                          # ExprE

    // Nível 8: Disjunção lógica (ou) (menor precedência)
    | expr OU expr                                         # ExprOu

    // Primários / Termos básicos
    | ABRE_PAREN expr FECHA_PAREN                          # ExprParenteses
    | literal                                              # ExprLiteral
    | IDENT                                                # ExprIdentificador
    ;

op_relacional
    : MENOR
    | MENOR_IGUAL
    | MAIOR
    | MAIOR_IGUAL
    | IGUAL
    | DIFERENTE
    ;

literal
    : INTEIRO
    | REAL
    | TEXTO
    | VERDADEIRO
    | FALSO
    ;

lista_argumentos
    : expr (VIRGULA expr)*
    ;
