// tipo_incompativel_soma.ml
// Erro semântico: tentar somar/concatenar texto com inteiro sem conversão.

vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
            texto ola.estado.mensagem = "Nível: " + 1

iniciar jornada com jornada.historias.ola
