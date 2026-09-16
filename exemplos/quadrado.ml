// quadrado.ml: a ronda de uma sentinela pelos quatro cantos de um pátio quadrado.
// Usa texto no estado, contagem com inteiros, cálculo com reais, se/senao aninhados,
// item de inventário e uma cena com cenário.

forte = Universo("forte")
    nome = "Forte do Pátio Quadrado"
    descricao = "Uma fortaleza com uma torre em cada canto do pátio."

    patio = forte.cenario("patio")
        nome = "Pátio Central"
        descricao = "Um quadrado de pedra com doze metros de lado."

    capita = forte.personagem("capita")
        nome = "Capitã Lúcia"
        descricao = "Comandante da guarda do forte."
        motivacao = "Garantir que nenhum canto fique sem vigia."

    guarda = forte.campanha("guarda")
        nome = "A Guarda do Forte"
        foco = "Rotina, atenção e pequenos mistérios."

        sentinela = guarda.jogador("sentinela")
            nome = "Tomé"
            descricao = "Sentinela novato do turno da noite."
            motivacao = "Provar que merece a armadura."
            inteiro sentinela.ficha.vigor = 4

            lampiao = sentinela.inventario.item("lampiao") // Item do inventário do jogador.
                nome = "Lampião"
                descricao = "Ilumina um lado do pátio por vez."

        ronda = guarda.historia("ronda")
            nome = "A Ronda Quadrada"
            objetivo = "Percorrer os quatro lados do pátio e voltar à torre norte."
            premissa = "A capitã exige uma volta completa antes do amanhecer."
            ronda.participantes.adicionar(forte.personagens.capita)
            ronda.participantes.adicionar(guarda.jogadores.sentinela)
            inteiro ronda.estado.lado = 0
            inteiro ronda.estado.voltas = 0
            texto ronda.estado.canto = "norte"
            inteiro ronda.estado.medida = 12
            real ronda.estado.area = 0.0
            real ronda.estado.diagonal = 0.0

            volta = ronda.marco("volta_completa")
                descricao = "Voltar à torre norte depois de passar pelos quatro cantos."
                concluir volta quando ronda.estado.voltas >= 1 e ronda.estado.canto == "norte"

            encerrar ronda quando volta.concluido

            operacao ronda.andar_um_lado // Não há módulo: o quarto lado zera a contagem.
                requer ronda.estado.voltas < 1
                ronda.estado.lado = ronda.estado.lado + 1
                se ronda.estado.lado == 1
                    ronda.estado.canto = "leste"
                senao
                    se ronda.estado.lado == 2
                        ronda.estado.canto = "sul"
                    senao
                        se ronda.estado.lado == 3
                            ronda.estado.canto = "oeste"
                        senao
                            ronda.estado.canto = "norte"
                            ronda.estado.lado = 0
                            ronda.estado.voltas = ronda.estado.voltas + 1
                narrar "A sentinela chega ao canto " + ronda.estado.canto + "."

            operacao ronda.medir_patio // Inteiro multiplicado por real resulta em real.
                requer ronda.estado.area == 0.0
                ronda.estado.area = ronda.estado.medida * ronda.estado.medida
                ronda.estado.diagonal = ronda.estado.medida * 1.41
                narrar "A sentinela mede o pátio com passos contados."

            muralha = ronda.capitulo("muralha")
                nome = "Sobre a Muralha"
                proposta = "Acompanhar a ronda de canto em canto."

                partida = muralha.cena("partida")
                    objetivo = "Começar a ronda pela torre norte."
                    contexto = "A capitã entrega o lampião e aponta para o leste."
                    local = patio
                    partida.participantes.adicionar(forte.personagens.capita)
                    partida.participantes.adicionar(guarda.jogadores.sentinela)

guarda = forte.campanhas.guarda
iniciar guarda com guarda.historias.ronda
