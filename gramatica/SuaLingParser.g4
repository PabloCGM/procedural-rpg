parser grammar SuaLingParser;

options {
    tokenVocab = SuaLing;
}

// Regra raiz temporária
programa
    : nova_linha* instrucao_bloco nova_linha* EOF
    ;

nova_linha
    : NOVA_LINHA
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

// ====================================================
// INSTRUÇÕES, COMANDOS E BLOCOS INDENTADOS (Passo 3)
// ====================================================

tipo_dado
    : TIPO_INTEIRO
    | TIPO_REAL
    | TIPO_TEXTO
    | TIPO_BOOLEANO
    ;

caminho_identificadores
    : IDENT (PONTO IDENT)+
    ;

atribuicao_simples
    : IDENT ATRIBUICAO expr
    ;

declaracao_estado
    : tipo_dado caminho_identificadores ATRIBUICAO expr
    ;

atribuicao_estado
    : caminho_identificadores ATRIBUICAO expr
    ;

chamada_metodo
    : expr PONTO IDENT ABRE_PAREN lista_argumentos? FECHA_PAREN
    ;

comando_narrar
    : NARRAR expr
    ;

comando_se
    : SE expr nova_linha* bloco_instrucoes (nova_linha* SENAO nova_linha* bloco_instrucoes)?
    ;

bloco_instrucoes
    : INDENTA (instrucao_bloco nova_linha*)+ DEDENTA
    ;

instrucao_bloco
    : comando_se
    | comando_narrar
    | declaracao_estado
    | atribuicao_estado
    | chamada_metodo
    | atribuicao_simples
    ;
