// ola.ml: o menor programa completo. Um universo, um jogador, uma história e uma operação.

vila = Universo("vila") // Raiz do mundo.
    nome = "Vila do Início"
    descricao = "Uma vila tranquila onde toda aventura começa."

    jornada = vila.campanha("jornada") // Campanha dentro do universo.
        nome = "Primeira Jornada"
        foco = "Apresentar a linguagem com o mínimo necessário."

        heroina = jornada.jogador("heroina") // Personagem jogável da campanha.
            nome = "Ana"
            descricao = "Uma aventureira recém-chegada à vila."
            motivacao = "Conhecer os moradores."

        ola = jornada.historia("ola") // A única história da campanha.
            nome = "Olá, mundo"
            objetivo = "Cumprimentar a vila."
            premissa = "Ana chega à praça central ao meio-dia."
            ola.participantes.adicionar(jornada.jogadores.heroina)
            booleano ola.estado.cumprimentou = falso

            saudacao = ola.marco("saudacao") // Único marco: cumprimentar.
                descricao = "Cumprimentar os moradores na praça."
                concluir saudacao quando ola.estado.cumprimentou

            encerrar ola quando saudacao.concluido

            operacao ola.cumprimentar // O motor solicita quando Ana cumprimenta alguém.
                requer nao ola.estado.cumprimentou
                ola.estado.cumprimentou = verdadeiro
                narrar "Olá, mundo!"

            praca = ola.capitulo("praca")
                nome = "A Praça"
                proposta = "Receber Ana na vila."

jornada = vila.campanhas.jornada
iniciar jornada com jornada.historias.ola
