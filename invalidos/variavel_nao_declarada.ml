// variavel_nao_declarada.ml
// Erro semântico: acessar identificador ou estado que não existe.

vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
            booleano ola.estado.cumprimentou = falso

            operacao ola.cumprimentar
                requer nao ola.estado.cumprimentou
                ola.estado.cumprimentou = verdadeiro
                narrar fantasma.mensagem

iniciar jornada com jornada.historias.ola
