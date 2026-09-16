// espiral.ml: descida por uma escadaria em espiral em que cada volta aumenta o perigo.
// Usa marcos encadeados, estado compartilhado do universo, divisão, sinal negativo,
// parênteses, condições com e/ou/nao e um NPC criado dentro de um capítulo.

abismo = Universo("abismo")
    nome = "O Abismo de Vesper"
    descricao = "Um poço sem fundo cercado por uma escadaria em espiral."
    booleano abismo.estado.selo_rompido = falso

    escadaria = abismo.cenario("escadaria")
        nome = "Escadaria Espiral"
        descricao = "Degraus de pedra que giram em torno do vazio."

    guardiao = abismo.personagem("guardiao")
        nome = "O Guardião"
        descricao = "Uma voz antiga que conta as voltas de quem desce."
        motivacao = "Impedir que o selo do fundo seja rompido."

    descida = abismo.campanha("descida")
        nome = "A Descida"
        foco = "Tensão crescente e escolhas arriscadas."

        mira = descida.jogador("mira")
            nome = "Mira"
            descricao = "Cartógrafa que desenha mapas de lugares impossíveis."
            motivacao = "Desenhar o mapa completo do abismo."
            inteiro mira.ficha.folego = 15
            real mira.ficha.coragem = 1.5

        espiral = descida.historia("espiral")
            nome = "A Espiral"
            objetivo = "Chegar ao fundo do abismo e decidir o destino do selo."
            premissa = "A cada volta, o raio da escadaria cai pela metade."
            espiral.participantes.adicionar(abismo.personagens.guardiao)
            espiral.participantes.adicionar(descida.jogadores.mira)
            inteiro espiral.estado.volta = 0
            real espiral.estado.raio = 16.0
            real espiral.estado.profundidade = 0.0
            real espiral.estado.tensao = -1.0

            primeira = espiral.marco("primeira_volta")
                descricao = "Completar a primeira volta da escadaria."
                concluir primeira quando espiral.estado.volta >= 1

            metade = espiral.marco("metade")
                descricao = "Chegar ao trecho em que o raio já caiu pela metade."
                metade.depende_de(primeira)
                concluir metade quando espiral.estado.raio <= 8.0

            fundo = espiral.marco("fundo")
                descricao = "Tocar o fundo do abismo."
                fundo.depende_de(metade)
                concluir fundo quando espiral.estado.raio < 2.0

            encerrar espiral quando abismo.estado.selo_rompido ou mira.ficha.folego <= 0

            operacao espiral.descer_uma_volta
                requer nao espiral.estado.raio < 2.0 e mira.ficha.folego > 0
                espiral.estado.volta = espiral.estado.volta + 1
                espiral.estado.raio = espiral.estado.raio / 2
                espiral.estado.profundidade = espiral.estado.profundidade + (16.0 - espiral.estado.raio) * 3.5
                espiral.estado.tensao = espiral.estado.tensao + 1.0
                mira.ficha.folego = mira.ficha.folego - 3
                se espiral.estado.tensao > 1.0
                    se mira.ficha.coragem >= 1.0
                        narrar "Mira respira fundo e continua descendo."
                    senao
                        narrar "Mira hesita diante do vazio."
                senao
                    narrar "A escadaria ainda parece segura."

            operacao espiral.descansar
                requer mira.ficha.folego < 15 e espiral.estado.volta != 0
                mira.ficha.folego = mira.ficha.folego + 2
                mira.ficha.coragem = mira.ficha.coragem - 0.25
                narrar "Mira descansa em um degrau, mas o vazio parece mais perto."

            operacao espiral.romper_selo // Consequência escrita explicitamente no universo.
                requer fundo.concluido e nao abismo.estado.selo_rompido
                abismo.estado.selo_rompido = verdadeiro
                narrar "O selo se parte e a escadaria começa a girar."

            trecho = espiral.capitulo("trecho")
                nome = "Volta Após Volta"
                proposta = "Descrever a descida e o estreitamento da escadaria."

                eco = trecho.personagem("eco") // NPC que pertence só a este capítulo.
                    nome = "Eco"
                    descricao = "Uma criança perdida que repete as últimas palavras ouvidas."
                    motivacao = "Encontrar a saída do abismo."

                degrau = trecho.cena("primeiro_degrau")
                    objetivo = "Apresentar a escadaria e o Guardião."
                    contexto = "O Guardião avisa que ninguém desceu mais de quatro voltas."
                    local = escadaria
                    degrau.participantes.adicionar(abismo.personagens.guardiao)
                    degrau.participantes.adicionar(descida.jogadores.mira)
                    degrau.participantes.adicionar(trecho.personagens.eco)

descida = abismo.campanhas.descida
iniciar descida com descida.historias.espiral
