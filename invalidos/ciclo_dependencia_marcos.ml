// ciclo_dependencia_marcos.ml
// Erro semântico: dependência cíclica entre marcos (m1 depende de m2 e m2 depende de m1).
// Erro esperado: linha 16, coluna 17, na dependência que fecha o ciclo.

vila = Universo("vila")
    jornada = vila.campanha("jornada")
        ola = jornada.historia("ola")
            booleano ola.estado.cumprimentou = falso

            m1 = ola.marco("m1")
                concluir m1 quando ola.estado.cumprimentou
                m1.depende_de(m2)

            m2 = ola.marco("m2")
                concluir m2 quando ola.estado.cumprimentou
                m2.depende_de(m1)

iniciar jornada com jornada.historias.ola
