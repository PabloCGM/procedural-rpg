parser grammar SuaLingParser;

options {
    tokenVocab = SuaLing;
}

// ====================================================
// REGRA RAIZ: PROGRAMA COMPLETO
// ====================================================
programa
    : nova_linha* (instrucao_topo nova_linha*)* comando_iniciar nova_linha* EOF
    ;

nova_linha
    : NOVA_LINHA
    ;

// ====================================================
// NÍVEL DE TOPO E DECLARAÇÃO DE ENTIDADES
// ====================================================
instrucao_topo
    : declaracao_entidade
    | declaracao_estado
    | atribuicao
    | expr
    ;

declaracao_entidade
    : IDENT ATRIBUICAO expr nova_linha* bloco_entidade
    ;

bloco_entidade
    : INDENTA (membro_entidade nova_linha*)+ DEDENTA
    ;

membro_entidade
    : declaracao_entidade
    | declaracao_operacao
    | regra_conclusao_marco
    | regra_encerramento_historia
    | declaracao_estado
    | atribuicao
    | expr
    ;

// ====================================================
// ESTADOS, FICHAS E ATRIBUIÇÕES
// ====================================================
declaracao_estado
    : tipo_dado caminho ATRIBUICAO expr
    ;

atribuicao
    : caminho ATRIBUICAO expr
    ;

tipo_dado
    : TIPO_INTEIRO
    | TIPO_REAL
    | TIPO_TEXTO
    | TIPO_BOOLEANO
    ;

caminho
    : IDENT (PONTO IDENT)*
    ;

// ====================================================
// MARCOS E PROGRESSO
// ====================================================
regra_conclusao_marco
    : CONCLUIR IDENT QUANDO expr
    ;

regra_encerramento_historia
    : ENCERRAR IDENT QUANDO expr
    ;

// ====================================================
// OPERAÇÕES NARRATIVAS
// ====================================================
declaracao_operacao
    : OPERACAO caminho nova_linha* bloco_operacao
    ;

bloco_operacao
    : INDENTA clausula_requer nova_linha* (instrucao_operacao nova_linha*)+ DEDENTA
    ;

clausula_requer
    : REQUER expr
    ;

instrucao_operacao
    : comando_se
    | comando_narrar
    | atribuicao
    | expr
    ;

bloco_instrucoes
    : INDENTA (instrucao_operacao nova_linha*)+ DEDENTA
    ;

comando_se
    : SE expr nova_linha* bloco_instrucoes (nova_linha* SENAO nova_linha* bloco_instrucoes)?
    ;

comando_narrar
    : NARRAR expr
    ;

// ====================================================
// COMANDO DE ABERTURA DE SESSÃO
// ====================================================
comando_iniciar
    : INICIAR expr COM expr
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
