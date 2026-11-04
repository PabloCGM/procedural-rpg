// metodo_receptor_invalido.ml
// Erro semântico: Campanha não possui método 'cenario' (apenas 'jogador' e 'historia').

vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
        guardiao = jornada.cenario("guardiao")

iniciar jornada com jornada.historias.ola
