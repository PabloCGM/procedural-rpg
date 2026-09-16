mundo = Universo("cidade_memorias") // Cria a raiz do universo.
    nome = "Cidade das Memórias" // Nome do universo.
    descricao = "Uma cidade onde lembranças são comercializadas." // Contexto do mundo.
    booleano mundo.estado.denuncia_publica = falso // Estado compartilhado.

    helena = mundo.personagem("helena") // NPC pertencente ao universo.
        nome = "Rainha Helena" // Nome da personagem.
        descricao = "Governante da Cidade das Memórias." // Identidade narrativa.
        motivacao = "Preservar a estabilidade do reino." // Motivação.

    arquivo = mundo.cenario("arquivo") // Cenário pertencente ao universo.
        nome = "Arquivo Real" // Nome do lugar.
        descricao = "Um acervo de registros sobre memórias." // Contexto do cenário.

    campanha = mundo.campanha("ecos") // Campanha dentro do universo.
        nome = "Ecos do Esquecimento" // Nome da campanha.
        foco = "Investigação e consequências narrativas." // Experiência pretendida.

        arin = campanha.jogador("arin") // Personagem do jogador nesta campanha.
            nome = "Arin" // Nome do personagem jogável.
            descricao = "Investigador de memórias perdidas." // Identidade narrativa.
            motivacao = "Descobrir quem está apagando o passado." // Motivação.
            inteiro arin.ficha.percepcao = 3 // Atributo inteiro da ficha.

        historia = campanha.historia("extracao") // História pertencente à campanha.
            nome = "A Extração" // Nome da história.
            objetivo = "Comprovar e denunciar a extração de memórias." // Fio condutor.
            premissa = "Registros no arquivo documentam uma extração clandestina." // Base estabelecida.
            historia.participantes.adicionar(mundo.personagens.helena) // Referência à rainha.
            historia.participantes.adicionar(campanha.jogadores.arin) // Referência ao jogador.
            inteiro historia.estado.provas = 0 // Progresso da investigação.
            real historia.estado.tensao = 0.5 // Medida real de tensão.
            booleano historia.estado.prova_entregue = falso // Controle da entrega.

            provas = historia.marco("reunir_provas") // Marco no escopo da história.
                descricao = "Obter uma prova documental da extração." // Avanço esperado.
                concluir provas quando historia.estado.provas >= 1 // Condição de conclusão.

            denuncia = historia.marco("denunciar") // Segundo marco da história.
                descricao = "Entregar a prova à rainha." // Avanço esperado.
                denuncia.depende_de(provas) // Dependência entre os marcos.
                concluir denuncia quando historia.estado.prova_entregue // Condição de conclusão.

            encerrar historia quando denuncia.concluido // Critério de encerramento.

            operacao historia.registrar_prova // Declara uma operação narrativa desta história.
                requer historia.estado.provas == 0 // Impede registrar a mesma prova novamente.
                historia.estado.provas = historia.estado.provas + 1 // Registra a descoberta aceita na sessão.
                historia.estado.tensao = historia.estado.tensao + 0.5 // Aplica a consequência local.

            operacao historia.entregar_prova // Declara outra operação, sem executá-la agora.
                requer provas.concluido e nao historia.estado.prova_entregue // Exige progresso anterior.
                mundo.estado.denuncia_publica = verdadeiro // Aplica uma consequência no universo.
                historia.estado.prova_entregue = verdadeiro // Registra a entrega efetivamente aceita.

            busca = historia.capitulo("busca") // Primeiro capítulo da história.
                nome = "Vestígios no Arquivo" // Nome do capítulo.
                proposta = "Buscar indícios da extração." // Função narrativa.

                iza = busca.personagem("iza") // NPC pertencente ao capítulo.
                    nome = "Iza" // Nome da personagem.
                    descricao = "Responsável pelos registros do arquivo." // Identidade.
                    motivacao = "Proteger as lembranças sob sua guarda." // Motivação.

            coroa = historia.capitulo("coroa") // Segundo capítulo da mesma história.
                nome = "A Denúncia" // Nome do capítulo.
                proposta = "Apresentar o que foi descoberto." // Função narrativa.

campanha = mundo.campanhas.ecos // Recupera a campanha fora do bloco do universo.
iniciar campanha com campanha.historias.extracao // Abre a sessão com a história explicitamente escolhida.
