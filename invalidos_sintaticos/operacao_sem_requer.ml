// operacao_sem_requer.ml: erro sintático pois toda operação exige 'requer' como primeira instrução
vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
            operacao ola.invalida
                narrar "faltou o requer"

jornada = vila.campanhas.jornada
iniciar jornada com jornada.historias.ola
