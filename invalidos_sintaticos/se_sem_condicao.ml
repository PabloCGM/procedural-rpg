// se_sem_condicao.ml: erro sintático pela falta da expressão booleana no 'se'
vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
            operacao ola.teste
                requer verdadeiro
                se
                    narrar "sem condicao"

jornada = vila.campanhas.jornada
iniciar jornada com jornada.historias.ola
