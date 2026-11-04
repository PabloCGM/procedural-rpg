// operacao_sem_booleano_requer.ml
// Erro semântico: a cláusula 'requer' deve ser booleana, mas recebeu número inteiro.

vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
            booleano ola.estado.cumprimentou = falso

            operacao ola.cumprimentar
                requer 42
                ola.estado.cumprimentou = verdadeiro
                narrar "Olá"

iniciar jornada com jornada.historias.ola
