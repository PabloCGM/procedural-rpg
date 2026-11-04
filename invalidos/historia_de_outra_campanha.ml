// historia_de_outra_campanha.ml
// Erro semântico: tentar iniciar campanha_a com historia_b pertencente a campanha_b.

vila = Universo("vila")
    camp1 = vila.campanha("camp1")
        h1 = camp1.historia("h1")

    camp2 = vila.campanha("camp2")
        h2 = camp2.historia("h2")

iniciar camp1 com camp2.historias.h2
