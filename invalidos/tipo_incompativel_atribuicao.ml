// tipo_incompativel_atribuicao.ml
// Erro semântico: atribuir texto a campo booleano.

vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
            booleano ola.estado.cumprimentou = "sim"

iniciar jornada com jornada.historias.ola
