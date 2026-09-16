# Ideia da linguagem — Procedural RPG

Registro da visão do projeto. As decisões abaixo atualizam as propostas anteriores; a sintaxe e o recorte acadêmico ainda não estão definidos.

## Propósito

O Procedural RPG é um motor de narrativas vivas. A linguagem será a base de expressão que uma IA poderá operar para construir e desenvolver campanhas, conectando a intenção do Mestre a informações e regras que um sistema consegue organizar, validar e executar.

O domínio é a narrativa de RPG, independente de um sistema específico de regras. A visão original inclui histórias adaptáveis a diferentes universos, causa e consequência, personagens coerentes e possíveis integrações externas. Essas integrações permanecem futuras e não ampliam o conjunto atual de entidades.

## Orientação a objetos e acesso por ponto

Decisões do autor: a linguagem será orientada a objetos; o operador `.` acessará membros de um objeto; a indentação será obrigatória para delimitar blocos, sem exigir `fim`. O escopo deve ficar explícito no objeto usado na criação, em vez de construções como `personagem de universo`.

Entidades serão objetos com identidade, atributos e métodos. Universo, Campanha, Historia, Capitulo, Cena e Personagem são candidatos a classes do domínio. A composição representa pertencimento, e referências permitem usar a mesma instância em diferentes contextos. O uso de `.` sozinho não define orientação a objetos: o modelo deverá especificar criação, tipos, estado, métodos e regras de acesso.

Proposta de sintaxe, ainda não definitiva:

```text
universo = Universo("Cidade das Memórias")

helena = universo.personagem("helena")
    nome = "Rainha Helena"
    motivacao = "Preservar a estabilidade do reino"

campanha = universo.campanha("ecos")
arin = campanha.jogador("arin")
    nome = "Arin"

historia = campanha.historia("memorias_roubadas")
varek = historia.personagem("varek")
    nome = "Varek"

historia.participantes.adicionar(universo.personagens.helena)
```

Nesse exemplo, `universo` é o nome de uma variável que referencia uma instância de Universo. `universo.personagem("helena")` é um método de criação que cria e registra um NPC naquele universo. `universo.personagens.helena` acessa a instância já registrada. A forma singular para o método e plural para a coleção é uma proposta, não uma regra final.

O bloco indentado após a criação configura os atributos do objeto recém-criado; sua resolução de nomes ainda deverá ser especificada. Referenciar um membro inexistente é erro, não criação implícita. O personagem local `helena` e o membro `universo.personagens.helena` apontam para a mesma instância.

Métodos de criação devem respeitar o domínio: a campanha permite criar personagens dos jogadores, mas não NPCs próprios; história, capítulo e cena podem criar NPCs. Marcos não criam personagens. Referenciar um personagem não altera seu pertencimento.

Classes definidas pelo usuário, herança, interfaces, polimorfismo, visibilidade e detalhes de encapsulamento ainda não foram escolhidos. A escolha de orientação a objetos não reintroduz automaticamente os moldes arbitrários suspensos. A compatibilização da indentação significativa com o requisito da E2 de descartar espaços em branco permanece a resolver.

## Hierarquia narrativa definida

```text
Universo
└── Campanhas
    └── Campanha
        └── Histórias
            └── História
                ├── Marcos narrativos conectados (controle de progresso)
                └── Capítulos
                    └── Capítulo
                        └── Cenas
                            └── Cena
                                ├── Cenário
                                └── Personagens participantes por referência
```

Um universo pode conter várias campanhas; uma campanha pode conter várias histórias. Uma história é o fio condutor pré-gerado que orienta seu desenvolvimento até o encerramento. Capítulos organizam o desenvolvimento narrativo; marcos pertencem à história e formam uma rede transversal de controle de progresso. A relação entre marcos e capítulos ocorre por referência, não por pertencimento. A organização de cenas em capítulos no diagrama é a proposta atual de composição; os marcos não são seus contêineres.

### Marcos transversais à história

Marcos são checkpoints que conectam o progresso da história. Não criam personagens nem funcionam como escopos de autoria narrativa. Devem expressar avanços coerentes com a história completa, sem serem definidos exclusivamente pelas necessidades de um capítulo.

Ser “cego ao capítulo” significa não depender de sua identidade ou de uma cena específica para caracterizar o progresso. Não significa ignorar o contexto, os fatos ou as consequências narrativas. A intenção é reduzir a tendência de cada capítulo forçar um caminho conveniente para cumprir seu próprio checkpoint; essa separação, sozinha, não garante ausência de viés na geração.

Proposta: cada marco descreve uma condição de progresso e suas dependências em outros marcos. Cenas de diferentes capítulos podem contribuir para ele. Exemplo: “obter evidência do envolvimento do conselheiro” pode ocorrer por investigação, conversa ou infiltração, sem exigir uma cena previamente fixada. A conclusão depende de evidência registrada no estado, e não apenas do encerramento de um capítulo.

Isso separa a árvore de pertencimento da rede de progresso da história. Regras para ramificações, alternativas, falhas, ciclos e critérios de conclusão ainda serão definidas.

Cenários e personagens compõem o contexto da cena. Para personagens, pertencimento e participação são distintos: cada personagem tem uma única definição canônica em seu escopo, enquanto histórias e cenas o referenciam. Os personagens participantes no diagrama não são necessariamente entidades pertencentes à cena. A localização canônica dos cenários ainda será definida.

## Entidades mantidas

| Elemento | Papel e relações |
|---|---|
| Universo | Identidade, regras, contexto e estado compartilhado do mundo; contém campanhas. |
| Campanha | Pertence ao universo, contém histórias e tem como personagens próprios exclusivamente os personagens dos jogadores. Pode ter estado local. |
| História | Objetivo e fio condutor pré-gerado; contém capítulos e marcos transversais. Pode definir ou referenciar NPCs. |
| Capítulo | Divisão narrativa da história; pode definir ou referenciar NPCs e se relaciona com marcos por referência. |
| Marco narrativo | Checkpoint pertencente à história, conectado a outros marcos; controla progresso sem pertencer a um capítulo ou criar personagens. |
| Cena | Situação procedural com cenário e participantes; pode definir ou referenciar NPCs e contribuir para o progresso dos marcos. |
| Cenário | Lugar com características estabelecidas; integra o contexto das cenas. |
| Estado | Situação atual e alterações de entidades, campanha e universo; gestão ainda em definição. |
| Personagem | Agente com identidade única e controle de jogador ou NPC. Jogáveis pertencem à campanha; NPCs podem pertencer ao universo, história, capítulo ou cena. Participações são referências. |
| Jogador/ficha | Ideia inicial de fichas dos personagens dos jogadores. Separar pessoa, personagem e ficha continua sendo uma possibilidade, não decisão fechada. |
| Item | Objeto com identidade e características definidas. |
| Inventário | Organiza itens associados a um proprietário; detalhes em aberto. |

Cenário significa lugar; cena significa situação ou acontecimento. Uma biblioteca pode ser usada em diferentes cenas.

As sugestões da antiga seção “Outras ideias de elementos” foram retiradas do modelo ativo. Moldes arbitrários e inferência de novos tipos também ficam suspensos: por enquanto, o foco é o modelo acima, acrescido de história e capítulo conforme a nova definição do autor. Isso não impede registrar informações como objetivos ou conhecimentos nos atributos das entidades existentes.

## Fluxo de criação

1. Definir o universo até que seu contexto seja considerado satisfatório.
2. Criar uma campanha dentro desse universo.
3. Criar os personagens dos jogadores dessa campanha.
4. Criar a primeira história considerando universo, estado atual e personagens.
5. Pré-gerar o esboço da história, capítulos e marcos narrativos.
6. Durante o jogo, gerar cenas consultando o contexto pertinente e os fatos estabelecidos.
7. Persistir os acontecimentos e mudanças; refletir no universo os efeitos que o alterarem.
8. Criar outras histórias na mesma campanha, mantendo a continuidade dos personagens.

Começar outra campanha implica criar novos personagens de jogador. Exceções como morte, substituição ou entrada de jogadores ainda não foram discutidas. NPCs do universo podem participar de diferentes campanhas e histórias por referência, sem serem recriados.

## Personagens: identidade, pertencimento e participação

### Controle e escopo

Personagem é uma única entidade conceitual. Duas características independentes descrevem seu uso:

- **Controle:** personagem de jogador (aquele que a pessoa joga) ou personagem não jogável (NPC).
- **Escopo de pertencimento:** indica onde a definição é mantida. Campanha é escopo exclusivo dos personagens dos jogadores; NPCs podem ser definidos no universo, história, capítulo ou cena. Marco narrativo não é escopo de criação de personagens.

| Escopo | Exemplo | Criação e persistência |
|---|---|---|
| Universo | Rainha Helena, relevante para diferentes campanhas | Definição mantida no universo e reutilizada por referência. |
| Campanha | Exclusivamente personagem do jogador | Criado ao iniciar a campanha e mantido entre suas histórias. NPCs recorrentes continuam referenciados a partir de seus próprios escopos. |
| História | Antagonista central de uma investigação | Definido na preparação da história e mantido em sua pasta. |
| Capítulo | NPC relevante para uma parte da história | Criado ou referenciado no contexto do capítulo. |
| Cena | Viajante incidental encontrado na estrada | Pode ser criado ao preparar a cena, antes de ser apresentado, e permanece registrado. |

O alcance não determina a frequência das aparições nem limita o impacto de suas ações. Um NPC local pode causar uma mudança global, e um personagem do universo pode aparecer uma única vez.

### Uma definição, várias referências

Cada personagem possui um identificador estável e uma única definição canônica. Nome exibido e caminho da pasta não são sua identidade. Histórias, capítulos e cenas referenciam esse identificador, sem copiar a ficha, a biografia ou as características do personagem. Um personagem criado num desses escopos pode participar de outros por referência, respeitando as regras de visibilidade que ainda serão definidas.

As informações se distribuem conforme sua responsabilidade:

| Registro | Informação que mantém |
|---|---|
| Definição do personagem | Quem ele é: identidade, características e motivações estabelecidas. |
| Participação na história | Referência ao personagem e seu papel planejado naquela história, incluindo momentos ou marcos previstos. |
| Participação no capítulo | Referência ao personagem e sua participação planejada naquela parte da história. |
| Participação na cena | Referência ao mesmo personagem e informações específicas daquele encontro. |
| Estado pertinente | Mudanças efetivamente ocorridas, vinculadas à identidade do personagem e ao contexto a que se aplicam. |

Exemplo conceitual: Helena é definida no universo. Uma história referencia Helena e planeja que ela receba provas no marco final. Uma cena de audiência referencia a mesma Helena e descreve o encontro. Nenhum desses registros cria uma segunda rainha ou redefine sua personalidade.

Um apelido local, como “rainha”, pode facilitar a referência sem criar outra entidade. A sintaxe desse mecanismo permanece em aberto. Referências diretas ou aliases devem resolver para a mesma identidade canônica.

### Contexto e estado

Para desenvolver uma cena, o sistema reúne seu contexto local, o planejamento pertinente da história, a definição dos personagens referenciados e o estado atual relevante. Essa composição pode ser temporária; não é necessário persistir outra ficha completa em cada cena.

Planejamento não é fato ocorrido: “Helena deverá receber as provas” orienta a história, mas só o acontecimento efetivo permite registrar “Helena recebeu as provas”. Mudanças como sua confiança no grupo são associadas ao personagem e ao grupo pertinente, sem substituir a definição por uma versão local divergente. A responsabilidade técnica de armazenar e aplicar essas mudanças continua em aberto.

### Criação e evolução do alcance

Pré-gerar um personagem significa completar e registrar suas informações obrigatórias antes de seu uso narrativo; não exige criar todos os NPCs antes do início da campanha. NPCs importantes ao planejamento são preparados antecipadamente; NPCs incidentais podem ser preparados antes de sua primeira cena.

Um NPC incidental que se torne recorrente pode continuar sendo referenciado ou ter seu escopo promovido, por exemplo de cena para história ou universo, preservando identidade e acontecimentos anteriores. Não passa a pertencer à campanha: esse escopo é exclusivo dos personagens dos jogadores. A política de promoção ainda será definida. Encerrar uma cena ou capítulo não apaga os personagens ali criados.

Um índice que associe identificadores às pastas é uma proposta técnica para permitir essas reorganizações sem quebrar referências; sua implementação não foi escolhida.

## Universo compartilhado e estados

A ideia atual é que o universo seja o guardião de seu estado. A campanha pode manter estado próprio, mas mudanças que afetem o universo devem aparecer no estado compartilhado. Exemplo: destruir uma ponte numa campanha muda a condição dessa ponte no universo, respeitando a cronologia que ainda será definida.

Essa decisão substitui a proposta anterior de isolar os efeitos das campanhas. Ainda falta definir quem valida e aplica mudanças, como sincronizar arquivos e como resolver campanhas simultâneas ou situadas em épocas diferentes. O componente responsável pelos estados não foi escolhido.

## Base sólida e espaço generativo

- **Sólido e pré-gerado:** identidade, características, relações e informações necessárias das entidades antes de seu uso narrativo, além do esboço da história, capítulos e marcos. NPCs incidentais podem ser preparados durante a campanha, antes de sua apresentação.
- **Generativo em tempo real:** cenas, diálogos, descrições e caminhos narrativos que respeitam os limites estabelecidos.
- **Persistente:** acontecimentos aceitos na narrativa devem ser guardados para orientar a continuidade. A regra de validação e incorporação desses fatos ainda será definida.

Sólido significa que a IA não deve reinterpretar ou reinventar o que já foi estabelecido. Isso permite transformações causadas pela história: as mudanças devem ser registradas explicitamente no estado, preservando identidade e causalidade.

A proposta é completar as informações necessárias de cada entidade. Nenhum conjunto finito de campos antecipa todas as perguntas possíveis; precisamos definir quais dados são obrigatórios e o procedimento para detalhes não previstos. A ausência de um campo não deve virar autorização implícita para contradizer a base.

## Procedimentos de criação das entidades

A IA deverá acessar funções que encapsulem o procedimento de criação de cada entidade: qual contexto consultar, quais informações gerar e quais requisitos cumprir para a entidade estar pronta.

Proposta técnica para cada procedimento:

1. Consultar ancestrais e referências pertinentes.
2. Gerar os campos exigidos pelo contrato da entidade.
3. Validar campos, tipos, referências e regras verificáveis.
4. Verificar compatibilidade com fatos narrativos existentes; a forma dessa revisão está aberta.
5. Persistir a entidade e devolver sua identificação.

Um esquema valida estrutura, mas não garante sozinho coerência literária. Nomes como `criar_universo`, `criar_personagem` e `criar_historia` são exemplos de ferramentas do motor, não funções implementadas nem palavras-chave já escolhidas.

## Estrutura lógica e persistência

A proposta inicial foi uma pasta por entidade. A discussão posterior abriu a possibilidade de a própria linguagem representar pertencimento e referências, usando nomes qualificados como `cidade_esquecida.personagens.helena`. Esses caminhos são lógicos e não precisam corresponder a pastas. A sintaxe e a resolução de nomes ainda serão definidas.

O armazenamento durável continua necessário, mas uma árvore de diretórios é uma alternativa, não uma exigência da linguagem. Arquivos ou banco de dados podem preservar o modelo e seu estado. A representação persistida será a fonte de verdade consultável, reduzindo a dependência da memória da conversa.

O conteúdo consultado ainda precisa entrar no contexto da geração. A diferença é buscar informações relevantes no armazenamento durável, sem reenviar continuamente todo o universo.

Exemplo de organização proposto, não implementado:

```text
universos/
└── universo_01/
    ├── contexto.md
    ├── estado.json
    ├── personagens/
    │   └── helena/
    │       └── contexto.md
    ├── cenarios/
    │   └── biblioteca/
    │       └── contexto.md
    └── campanhas/
        └── campanha_01/
            ├── contexto.md
            ├── estado.json
            ├── personagens/
            │   └── personagem_01/
            │       ├── contexto.md
            │       ├── ficha.json
            │       └── inventario/
            └── historias/
                └── historia_01/
                    ├── contexto.md
                    ├── referencias.json
                    ├── personagens/
                    │   └── antagonista_01/
                    │       └── contexto.md
                    ├── marcos/
                    │   └── marco_01/
                    │       └── contexto.md
                    └── capitulos/
                        └── capitulo_01/
                            ├── contexto.md
                            ├── referencias.json
                            ├── personagens/
                            │   └── npc_do_capitulo/
                            │       └── contexto.md
                            └── cenas/
                                └── cena_01/
                                    ├── contexto.md
                                    ├── referencias.json
                                    └── personagens/
                                        └── viajante_01/
                                            └── contexto.md
```

Os personagens ficam em seu escopo de pertencimento; os arquivos de referências da história e da cena apontam para as definições pertinentes, inclusive as do universo. A posição dos cenários continua sendo uma sugestão. Markdown/JSON, nomes dos arquivos, localização dos itens e convenção de identificadores não estão fechados. Tipos de entidade agrupam instâncias; cada instância tem sua pasta. Nenhuma pasta de dados foi criada nesta discussão.

## Conceitos relacionados e referências

A proposta combina modelagem de domínio, composição hierárquica, referências entre entidades, persistência em arquivos, fonte de verdade canônica, contratos de criação e geração narrativa condicionada por planejamento e estado.

- **Linguagem específica de domínio (DSL):** o ink é uma linguagem existente para narrativas interativas. É uma referência de linguagem narrativa, não evidência de um sistema idêntico ao proposto: https://www.inklestudios.com/ink/
- **Memória externa e recuperação sob demanda:** contexto relevante pode ser localizado e lido durante a execução do agente. Isso se aproxima da consulta aos arquivos proposta aqui: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Esquemas e contratos de dados:** JSON Schema exemplifica validação de propriedades, tipos e campos obrigatórios. Não foi escolhido como tecnologia do projeto: https://json-schema.org/understanding-json-schema/reference/object
- **Agentes generativos com memória e planejamento:** o trabalho Generative Agents investiga armazenamento de experiências, recuperação, reflexão e planejamento. É uma referência parcial, não uma implementação desta hierarquia de campanhas: https://arxiv.org/abs/2304.03442

A pesquisa identificou componentes e abordagens semelhantes, sem estabelecer a existência de um produto que implemente exatamente toda esta combinação.

## Relação com a entrega acadêmica

A visão completa envolve linguagem, persistência, procedimentos de autoria e IA. A E2 exige especificar uma linguagem pequena, criar lexer em ANTLR, listar tokens com localização de erros e fornecer três exemplos válidos e três inválidos, além da documentação do repositório.

A hierarquia ajuda a planejar a sintaxe; as relações ajudam a planejar a semântica. E2 reconhece tokens; E3 valida estrutura sintática; E4 valida referências e tipos e executa o recorte escolhido. Integração com IA, persistência completa e geração procedural não estão assumidas como entregas da E2.

## Decisões pendentes

- Atributos obrigatórios e espaços generativos de cada entidade.
- Como os marcos orientam a história e permitem caminhos diferentes.
- Localização canônica de cenários e itens; política de promoção de escopo dos personagens e resolução de suas referências.
- Responsável por validar e aplicar mudanças de estado e propagá-las ao universo.
- Cronologia e conflitos entre campanhas.
- Critério para incorporar detalhes gerados à base sólida.
- Tratamento de informações necessárias não previstas na criação.
- Formatos de arquivo, identificadores e mecanismos de consulta.
- Nome definitivo da linguagem, extensão, sintaxe, tipos, comandos e operadores.
- Recorte da disciplina e três exclusões explícitas da linguagem.

O domínio precisa ser comunicado e aprovado conforme o enunciado. “Procedural RPG” permanece o nome de trabalho da proposta.
