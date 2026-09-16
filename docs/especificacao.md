# Especificação da linguagem Procedural RPG

Parte A — E2 · Versão inicial da linguagem · Extensão dos programas: `.ml`.

## 1. Finalidade da linguagem em duas frases

Procedural RPG é uma linguagem orientada a objetos de domínio específico para descrever universos, personagens e histórias de campanhas de RPG, preservando a identidade das entidades e suas relações. Ela permite que um Mestre ou uma IA escreva programas que iniciam sessões interativas, oferecem operações narrativas e acompanham marcos, enquanto um motor desenvolve as cenas conforme as ações dos jogadores e o estado do mundo.

## 2. Programa completo comentado linha a linha

O programa prepara uma campanha de investigação, define sua base narrativa e inicia uma sessão. Ele não determina uma sequência de cenas nem afirma antecipadamente que o jogador encontrará a prova: oferece operações que o motor poderá solicitar quando os acontecimentos da sessão as justificarem. Todos os nomes são declarados antes do uso; cada linha de código possui um comentário explicativo.

```text
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
```

Ao iniciar, os valores permanecem nos estados declarados: nenhuma prova foi obtida, nenhum marco foi concluído e nenhuma denúncia se tornou pública. A sessão aguarda interações; declarar operações, capítulos e personagens não executa seus acontecimentos.

Um percurso possível é o jogador investigar o arquivo ou convencer Iza a fornecer um registro. Depois que essa descoberta for aceita no contexto da sessão, o motor solicita `registrar_prova` ao interpretador; o resultado é uma prova, tensão `1.0` e conclusão do primeiro marco. Se, posteriormente, o jogador entregar a prova à rainha e essa ocorrência for aceita, o motor solicita `entregar_prova`; a denúncia passa a ser pública, o segundo marco conclui e a história encerra. A tentativa de entregar a prova antes de obtê-la é rejeitada sem alterações de estado.

Essas são consequências condicionais, não uma saída fixa do programa: sem essas interações, a história não avança automaticamente. A cena em que cada operação se torna pertinente é desenvolvida pelo motor, podendo variar conforme o caminho escolhido. O exemplo é completo como definição de campanha e ponto de entrada de uma sessão; executar a experiência exige o motor de interação descrito na seção 4.6, que não é a entrega do lexer da E2.

## 3. Tipos de dados

### 3.1. Valores primitivos

| Tipo | Valores e literais | Regras |
|---|---|---|
| `inteiro` | `0`, `3`, `150` | Sequência de algarismos decimais; o sinal negativo é um operador separado. |
| `real` | `0.5`, `12.75` | Exige algarismos antes e depois do ponto; não aceita vírgula decimal nem notação exponencial nesta versão. |
| `texto` | `"Rainha Helena"` | Aspas duplas; aceita Unicode no conteúdo e os escapes `\"`, `\\`, `\n` e `\t`. Não aceita quebra física de linha dentro do literal. |
| `booleano` | `verdadeiro`, `falso` | Condições exigem esse tipo; números e textos não são convertidos implicitamente em booleanos. |

Inteiros não possuem limite fixo de tamanho nesta versão. Reais seguem representação de ponto flutuante de dupla precisão; comparações reais usam os valores representados, sem tolerância implícita. A promoção de `inteiro` para `real` é permitida; a conversão inversa e conversões entre texto, booleano e número não são implícitas. Não há valor nulo.

Identificadores seguem `[a-zA-Z_][a-zA-Z_0-9]*`, distinguem maiúsculas de minúsculas e não podem ser palavras reservadas. Nomes apresentados ao usuário podem conter acentos por serem textos. Identificadores passados aos métodos de criação são literais de texto cujo conteúdo também segue essa regra, permitindo acesso como `mundo.personagens.helena`.

### 3.2. Objetos do domínio

A linguagem possui classes predefinidas com identidade, atributos e métodos. Os programas instanciam e relacionam esses objetos; não declaram classes arbitrárias. A implementação utiliza composição e referências, com encapsulamento das identidades, coleções e indicadores de progresso.

| Classe | Pertencimento e responsabilidade |
|---|---|
| `Universo` | Raiz do mundo; contém campanhas, NPCs, cenários e estado compartilhado. |
| `Campanha` | Pertence a um universo; contém histórias e exclusivamente personagens dos jogadores como personagens próprios. |
| `Historia` | Pertence a uma campanha; contém capítulos, marcos transversais, NPCs, participantes e estado local. |
| `Capitulo` | Pertence a uma história; contém cenas e NPCs e pode referenciar participantes. |
| `Marco` | Pertence a uma história; controla progresso e dependências, sem criar personagens ou pertencer a capítulos. |
| `Cena` | Pertence a um capítulo; registra uma situação com contexto, cenário, participantes e NPCs locais. Pode ser criada pelo motor durante a sessão. |
| `Cenario` | Pertence ao universo; pode ser referenciado por várias cenas. |
| `Personagem` | Representa NPC ou personagem jogável, com controle e proprietário definidos na criação. |
| `Estado` | Registro de campos tipados de um universo, campanha ou história. |
| `Ficha` | Registro de campos tipados de um personagem jogável. |
| `Inventario` | Contém itens pertencentes a um personagem. |
| `Item` | Objeto narrativo com identidade; nesta versão, permanece no inventário em que foi criado. |

Um `Estado` é criado automaticamente para cada universo, campanha e história. Todo personagem recebe um `Inventario`; somente personagens jogáveis recebem `Ficha`. Esses objetos são acessados por `.estado`, `.inventario` e `.ficha`, sem construtores adicionais no programa. As coleções como `.personagens`, `.jogadores` e `.participantes` são membros internos com acesso controlado, não tipos de coleção genéricos declarados pelo usuário.

### 3.3. Atributos e referências

Todas as entidades nomeadas possuem `id`, `nome` e `dono`. `id` e `dono` são somente leitura; `nome` começa com o identificador e pode ser configurado como texto. O universo não expõe `dono`, pois é a raiz.

| Classe | Campos adicionais da definição |
|---|---|
| `Universo`, `Cenario`, `Item` | `descricao: texto`, obrigatória. |
| `Campanha` | `foco: texto`, obrigatório. |
| `Historia` | `objetivo: texto` e `premissa: texto`, obrigatórios; `encerrada: booleano`, inicialmente falso e somente leitura. |
| `Capitulo` | `proposta: texto`, obrigatória. |
| `Marco` | `descricao: texto`, obrigatória; `concluido: booleano`, inicialmente falso e somente leitura. |
| `Cena` | `objetivo: texto`, `contexto: texto` e `local: Cenario`, obrigatórios; `encerrada: booleano`, inicialmente falso e mantido pelo motor, sem atribuição direta no programa. |
| `Personagem` | `descricao: texto` e `motivacao: texto`, obrigatórias; `controle: texto`, somente leitura, com valor `"jogador"` ou `"npc"`. |

Campos textuais obrigatórios não aceitam texto vazio. A definição precisa estar completa ao terminar o bloco de criação. Após esse bloco, atributos da definição não podem ser reescritos nesta versão; mudanças narrativas são representadas em campos de estado, sem reinventar a identidade. Referências não autorizam alterar membros protegidos.

Uma associação como `rainha = mundo.personagens.helena` cria um nome para a mesma instância, sem copiá-la ou alterar seu proprietário. Cada nome é associado uma única vez em seu escopo léxico e fica disponível, a partir da declaração, nesse bloco e nos blocos internos. Um bloco interno pode consultar os nomes dos escopos superiores, mas não pode redeclarar um nome já visível; blocos separados podem usar o mesmo nome local. Atributos configurados por nome simples, como `nome`, não são variáveis locais.

Nomes locais não ficam disponíveis diretamente fora de seu bloco. O objeto continua acessível por seu caminho público: fora do universo, `mundo.campanhas.ecos` recupera a campanha. O exemplo associa esse caminho a um novo nome `campanha` no nível principal; esse nome e o usado dentro do universo referenciam a mesma instância, em escopos distintos. As operações e condições registradas preservam as referências de seu escopo de declaração.

Coleções são consultadas por identificador e rejeitam acessos inexistentes; criar duas entidades com o mesmo identificador na mesma coleção também é erro. Identificadores iguais em coleções diferentes são permitidos, e o caminho distingue as entidades.

NPCs podem ser criados somente no universo, história, capítulo ou cena. Personagens jogáveis são criados somente na campanha. Histórias, capítulos e cenas podem adicionar participantes do seu universo, mas personagens jogáveis devem pertencer à campanha da história em questão; NPCs pertencentes a outra campanha não podem ser usados diretamente, enquanto NPCs do universo podem ser compartilhados. Um personagem criado na história continua existindo após o encerramento dela.

## 4. Comandos

### 4.1. Organização do programa e indentação

O arquivo usa UTF-8. Cada instrução ocupa uma linha física; não há `;`, chaves, `fim` ou continuação de instrução em várias linhas. Um bloco começa na linha seguinte ao seu cabeçalho com quatro espaços a mais; termina quando a indentação retorna a um nível anterior. Tabulações fora de textos são inválidas. Linhas vazias e linhas contendo apenas comentários não abrem nem fecham blocos.

Há blocos de definição de objetos, operações narrativas e condicionais. Um bloco não pode ser vazio. A definição de uma entidade filha deve estar diretamente dentro do bloco de seu proprietário: campanha dentro de universo, história dentro de campanha, capítulo dentro de história e cena dentro de capítulo. Marcos ficam diretamente na história, no mesmo nível dos capítulos. NPCs ficam no bloco de seu proprietário permitido; personagens jogáveis ficam na campanha. Itens são declarados dentro do personagem proprietário, usando seu inventário como receptor.

A indentação e o receptor da criação precisam concordar. Dentro de um capítulo, `historia.personagem(...)` não pode criar um NPC da história: essa declaração deve estar no bloco da história. Referenciar entidades de outros escopos continua permitido pelas regras de visibilidade e participação. Assim, o aninhamento mostra pertencimento sem duplicar personagens compartilhados.

Espaços de separação e comentários são descartados como conteúdo. A estrutura de linhas e níveis de indentação é preservada como informação de layout, conceitualmente `NOVA_LINHA`, `INDENTA` e `DEDENTA`, sem gerar tokens para cada espaço. O processamento léxico deve medir o recuo antes de descartá-lo, ignorar linhas vazias/comentadas e fechar os níveis restantes no final do arquivo. Esse tratamento explicita a adaptação necessária ao requisito do enunciado sobre descarte de espaços; descartá-los indiscriminadamente antes de medir o recuo destruiria a sintaxe escolhida.

### 4.2. Criação de objetos e métodos

`nome = Universo("id")` cria uma raiz no nível principal. Os demais objetos são criados por métodos do proprietário, na forma `nome = receptor.metodo("id")`, seguidos obrigatoriamente por seu bloco de definição. Nesse bloco, `nome = "Helena"`, por exemplo, configura o atributo do objeto em criação, não declara uma variável.

Um bloco de definição pode configurar os atributos do próprio objeto, declarar seus campos de estado ou ficha, criar entidades filhas permitidas, associar referências e registrar participantes, dependências e condições pertinentes ao objeto. Histórias também podem declarar operações narrativas. Definir um objeto não inicia uma sessão nem produz narração imediatamente. Dentro do bloco de um marco são registradas sua condição e suas dependências; dentro do bloco de uma cena, seu contexto e seus participantes.

Ao abrir a definição, o objeto e seu nome ficam disponíveis para construir seu conteúdo e acessar seus componentes automáticos. Campos obrigatórios precisam estar preenchidos ao fechar o bloco; ler um campo antes de sua inicialização é erro. Nenhuma interação da sessão é processada enquanto as definições iniciais estão sendo construídas. O nome usado para uma nova referência local não pode coincidir com um atributo do objeto em definição, evitando ambiguidade com configuração de atributos.

| Receptor | Método de criação | Resultado e coleção de acesso |
|---|---|---|
| `Universo` | `campanha("id")` | `Campanha`, registrada em `.campanhas.id`. |
| `Universo` | `cenario("id")` | `Cenario`, registrado em `.cenarios.id`. |
| `Universo`, `Historia`, `Capitulo`, `Cena` | `personagem("id")` | NPC `Personagem`, registrado em `.personagens.id`. |
| `Campanha` | `jogador("id")` | `Personagem` jogável, registrado em `.jogadores.id`. |
| `Campanha` | `historia("id")` | `Historia`, registrada em `.historias.id`. |
| `Historia` | `capitulo("id")` | `Capitulo`, registrado em `.capitulos.id`. |
| `Historia` | `marco("id")` | `Marco`, registrado em `.marcos.id`. |
| `Capitulo` | `cena("id")` | `Cena`, registrada em `.cenas.id`. |
| `Inventario` | `item("id")` | `Item`, registrado em `.itens.id`. |

Métodos de criação não listados são inválidos. Não existe `campanha.personagem(...)` nem criação de personagens em marcos. Tipos, quantidade de argumentos, identificadores e campos obrigatórios são verificados antes de iniciar a sessão; definições adicionadas pelo motor recebem as mesmas verificações antes de entrar no contexto narrativo. Além dos métodos predefinidos, somente operações narrativas declaradas conforme a seção 4.5 podem ser solicitadas durante a interação.

`objeto.participantes.adicionar(personagem)` adiciona uma referência aos participantes de uma história, capítulo ou cena. Adicionar novamente a mesma instância não a duplica. A participação na história não inclui automaticamente o personagem em todas as cenas: cada cena declara explicitamente seus participantes.

`marco.depende_de(outro_marco)` registra um pré-requisito. Ambos devem pertencer à mesma história; dependências próprias e ciclos são erros. Várias chamadas representam dependências cumulativas: todas precisam estar concluídas.

### 4.3. Declaração e atualização de dados

`tipo objeto.estado.campo = expressao` declara um campo com tipo primitivo e valor inicial dentro da definição do objeto que possui esse estado. `tipo personagem.ficha.campo = expressao` faz o mesmo dentro da definição do personagem jogável. Campos não podem ser redeclarados nem aparecer sem inicialização.

Dentro de uma operação narrativa, `objeto.estado.campo = expressao` atualiza um campo previamente declarado, respeitando seu tipo. Atribuições aos campos de ficha são permitidas com a mesma regra. Durante a sessão, alterações nesses dados passam pelas operações declaradas, sem escrita direta pela IA. Atribuir a um campo inexistente não o cria. Nomes curtos de campos não são procurados implicitamente em estados ancestrais: usa-se o caminho explícito.

O receptor determina o alcance da mudança: `historia.estado.provas = 1` é local; `mundo.estado.denuncia_publica = verdadeiro` modifica o universo compartilhado. O motor não infere, a partir de texto narrado, que um campo local deve ser copiado para o universo. O programa deve escrever explicitamente a consequência global quando ela existir; todas as referências ao mesmo universo passam a observar esse valor.

### 4.4. Progresso narrativo

`concluir marco quando condicao` registra exatamente uma condição booleana por marco. A condição não é avaliada uma única vez na declaração: ela é consultada ao iniciar a sessão e após a aplicação bem-sucedida de cada operação narrativa. Um marco conclui quando sua condição e todas as suas dependências forem satisfeitas. A conclusão permanece verdadeira mesmo que os valores usados na condição mudem depois.

Quando um marco conclui, as dependências são reavaliadas até não haver novas conclusões. Em seguida, `encerrar historia quando condicao` determina se a história termina. Cada história possui exatamente uma condição de encerramento; ela pode combinar vários marcos com operadores booleanos. O encerramento também é permanente.

Condições registradas não possuem efeitos colaterais: podem ler valores e aplicar operadores, mas não criar objetos nem solicitar operações. Marcos não possuem um capítulo proprietário; acontecimentos de qualquer cena da história podem justificar operações que contribuam para sua conclusão. Terminar um capítulo não conclui marcos automaticamente. Nem a ordem dos capítulos nem uma cena específica são pré-requisitos implícitos dos marcos.

### 4.5. Operações narrativas

`operacao historia.identificador` declara, diretamente no bloco da história, uma operação narrativa vinculada àquela instância. É uma declaração de comportamento com efeitos controlados, não uma nova entidade da árvore nem uma chamada imediata. O identificador deve ser único entre os membros daquela história; não pode substituir atributos ou métodos predefinidos. Nesta versão, operações não recebem parâmetros nem retornam valores.

A primeira linha do bloco é obrigatoriamente `requer condicao`, com expressão booleana sem efeitos colaterais. Depois dela, o bloco contém uma ou mais atribuições a estado/ficha, instruções `narrar` ou condicionais. O motor pode consultar a condição para informar quais operações estão habilitadas, mas o interpretador a verifica novamente no momento de cada solicitação.

`narrar expressao` exige `texto` e emite uma mensagem ao motor após a operação ser aceita. `se condicao` executa seu bloco quando a condição booleana é verdadeira; `senao`, opcional e alinhado com o `se` correspondente, executa o outro bloco. Condicionais podem ser aninhados. O bloco acessa os nomes já declarados no seu contexto e nos contextos superiores.

Ao receber uma solicitação, o interpretador verifica a história ativa, sua situação de encerramento e o requisito da operação. Se o requisito for falso, a solicitação é rejeitada sem alterações. Se for verdadeiro, as instruções são avaliadas em ordem, de modo que uma instrução veja as alterações anteriores do mesmo bloco; somente o sucesso do bloco inteiro confirma as alterações e libera as mensagens. Erro de execução descarta as alterações e mensagens daquela operação. Após a confirmação, marcos e encerramento são reavaliados. Operações não podem criar entidades nem chamar outras operações.

Repetir uma solicitação implica verificar novamente seu requisito. Não existe conclusão automática por mencionar uma operação na narração. No exemplo, `provas == 0` impede contabilizar a mesma prova mais de uma vez; `nao prova_entregue` impede uma segunda entrega. Solicitações são processadas uma por vez, sem concorrência nesta versão.

As condições formais verificam o estado, mas não provam que um acontecimento descrito em linguagem natural ocorreu. Reconhecer que o jogador realmente obteve uma prova e associar isso à operação correta é responsabilidade do motor, com confirmação narrativa do Mestre ou mecanismo equivalente de adjudicação. A sugestão da IA, isoladamente, não altera o estado.

### 4.6. Início da sessão e contrato com o motor

`iniciar campanha com historia` é a última instrução do nível principal e aparece uma única vez no programa. Seus operandos devem referenciar uma campanha e uma história pertencente a ela. A preparação valida o programa inteiro, inclusive operações ainda não solicitadas; em seguida, o interpretador disponibiliza ao motor os objetos, as referências, os estados, os marcos e as operações da história escolhida. As condições iniciais são avaliadas, e uma história já encerrada não inicia uma nova sessão de jogo.

O comando abre uma sessão e aguarda interações. Não percorre capítulos automaticamente, não escolhe uma lista fixa de cenas e não executa todas as operações habilitadas. Capítulos fornecem contexto e organização; os marcos e o estado fornecem restrições de progresso. Ao encerrar a história, o motor interrompe novas solicitações a ela; a campanha e seus personagens continuam existindo. Iniciar outra história da campanha é uma decisão explícita do motor, não um salto automático no código.

O contrato de integração possui estas responsabilidades:

| Componente | Responsabilidade |
|---|---|
| Linguagem | Expressar a base narrativa, as relações, as condições e os efeitos permitidos. |
| Interpretador | Validar definições, resolver referências, aplicar operações e calcular o progresso. |
| Motor da sessão | Receber ações dos jogadores, reunir contexto, manter a cena atual, adjudicar ocorrências e solicitar operações ao interpretador. |
| IA, quando conectada | Propor cenas, diálogos e desenvolvimentos coerentes com o contexto, sem reescrever fatos ou estados diretamente. |

Em cada interação, o motor consulta o contexto relevante, apresenta ou desenvolve uma cena, recebe a ação do jogador e determina suas consequências. Quando uma consequência corresponde a uma operação declarada, envia ao interpretador a identidade da história e o nome da operação; recebe aceitação ou rejeição, mudanças de estado, mensagens e marcos concluídos. O motor registra a ocorrência e produz a resposta ao jogador com base no resultado confirmado. Uma interação puramente descritiva pode continuar sem solicitar nenhuma operação; consequências não representáveis pelas operações desta versão não são inventadas como mudanças de estado.

A criação procedural ocorre pela interface de autoria do motor: ele pode submeter novas cenas e NPCs incidentais aos proprietários permitidos da história ativa, usando as mesmas classes, atributos, referências e validações da linguagem. Esses objetos são preparados e registrados antes de sua primeira apresentação. A adição não modifica a definição de entidades existentes, não redefine campos de estado, operações ou marcos e não cria identidades duplicadas. A hierarquia lógica da definição deve corresponder ao proprietário, mesmo quando a interface envia apenas uma nova subárvore. Referências são resolvidas no contexto do proprietário e em caminhos explícitos; não se inventam variáveis locais de definições anteriores.

Uma cena possui contexto e participantes, pode conter várias interações e só é encerrada quando o motor registra o fim daquela situação. Ela pode contribuir para nenhum, um ou vários marcos, sem possuir esses marcos. Diálogos ou caminhos diferentes podem levar à mesma operação válida. O contexto registrado da cena e o registro das ocorrências preservam o que passou a ser fato; planejar uma audiência não significa que a audiência ocorreu.

A interface concreta do motor não faz parte da sintaxe da linguagem: pode ser um terminal com um Mestre selecionando contextos e operações, ou uma aplicação com IA. Sem um adaptador de sessão, `iniciar` deve informar a ausência desse componente, em vez de simular progresso. Para demonstrar o interpretador na E4, um adaptador local pode conduzir interações e solicitações manualmente, sem serviços externos. A E2 entrega a especificação e o reconhecimento léxico, não esse motor nem a integração com IA. Persistência durável e sincronização de campanhas simultâneas continuam sendo responsabilidades posteriores do motor; os registros e objetos permanecem disponíveis durante a sessão.

Palavras reservadas desta versão: `inteiro`, `real`, `texto`, `booleano`, `verdadeiro`, `falso`, `concluir`, `quando`, `encerrar`, `operacao`, `requer`, `iniciar`, `com`, `narrar`, `se`, `senao`, `e`, `ou`, `nao`. `Universo` é um nome predefinido protegido; nomes de classes, métodos, operações e atributos são reconhecidos lexicalmente como identificadores e validados semanticamente conforme seu uso. Não há comando `executar` nem bloco `ao executar` nesta versão.

## 5. Operadores e precedência

Da maior precedência para a menor:

| Nível | Operadores | Significado e associação |
|---|---|---|
| 1 | `.` e chamada `(...)` | Acesso a membros e chamada de métodos/construtor; encadeamento da esquerda para a direita. |
| 2 | `+` e `-` unários | Sinal de um valor numérico; associação à direita. |
| 3 | `*`, `/` | Multiplicação e divisão numéricas; associação à esquerda. |
| 4 | `+`, `-` binários | Adição e subtração numéricas; `+` também concatena dois textos; associação à esquerda. |
| 5 | `<`, `<=`, `>`, `>=`, `==`, `!=` | Comparações; não associativas, sem encadeamentos como `1 < x < 5`. |
| 6 | `nao` | Negação booleana; associação à direita. |
| 7 | `e` | Conjunção booleana com curto-circuito; associação à esquerda. |
| 8 | `ou` | Disjunção booleana com curto-circuito; associação à esquerda. |

Parênteses também agrupam expressões e podem alterar a ordem padrão. `=` é atribuição ou inicialização no contexto de uma instrução, não um operador de expressão: não há atribuição encadeada nem atribuição dentro de condições. A vírgula separa argumentos; não é um operador de cálculo.

`+`, `-` e `*` retornam inteiro quando ambos os operandos são inteiros e real quando ao menos um é real. `/` sempre retorna real; divisão por zero é erro. Não existe divisão inteira nem módulo nesta versão.

Comparações de ordem aceitam somente números. Igualdade aceita números compatíveis, dois textos, dois booleanos ou duas referências da mesma classe; referências são iguais quando apontam para a mesma instância. Objetos internos como coleções não participam de comparações. Operações entre tipos incompatíveis são erros; concatenar texto com número exige reformular a saída, pois não há conversão automática.

Exemplos: `2 + 3 * 4` resulta em `14`; `(2 + 3) * 4` resulta em `20`; `nao historia.estado.provas >= 3` equivale a `nao (historia.estado.provas >= 3)`. O ponto em `0.5` faz parte do literal real; em `mundo.estado`, é acesso a membro.

## 6. Comentários

Comentários começam com `//` e terminam antes da quebra de linha. Podem ocupar uma linha inteira ou aparecer após uma instrução; o conteúdo do comentário é descartado e não altera o estado nem a indentação dos blocos.

Dentro de texto entre aspas, `//` permanece parte do literal, como em `"https://exemplo"`. Não há comentários de bloco. O símbolo `/` isolado representa divisão.

Erros léxicos devem indicar linha e coluna: caractere não reconhecido, tabulação estrutural, texto não fechado, escape inválido ou literal numérico malformado. Nesta linguagem, `3.`, `.5`, `1.2.3`, `12abc` e `1e3` são formas numéricas inválidas e não devem ser aceitas silenciosamente como sequências úteis de outros tokens. Regras de erro devem preservar a distinção entre literais numéricos e o ponto de acesso a membros.

Erros de indentação pertencem ao processamento do layout; referências inexistentes, tipos incompatíveis, métodos inválidos e ciclos de marcos são erros posteriores, não tarefas do reconhecimento de tokens da E2.

## 7. Três coisas que a linguagem deliberadamente não faz

1. **Não incorpora um modelo de IA nem interpreta livremente as intenções dos jogadores.** O interpretador oferece definições e operações verificáveis; a interpretação das ações e a geração procedural pertencem ao motor conectado. Uma IA pode escrever o programa e propor cenas durante a sessão, mas suas propostas precisam passar pelo contrato de autoria e interação antes de integrar os fatos e estados do mundo.
2. **Não implementa um sistema de combate, dados ou regras de um RPG específico.** Fichas guardam valores declarados pelo autor, mas não calculam regras de Dungeons & Dragons ou de outro sistema. O foco é a estrutura e a progressão narrativa.
3. **Não oferece programação orientada a objetos de propósito geral.** O usuário opera classes narrativas predefinidas e declara operações de história com requisitos e efeitos, sem classes próprias, herança, funções genéricas ou recursão. O programa não acessa diretamente serviços externos, dispositivos, arquivos ou bancos de dados; essas integrações, quando presentes, pertencem ao motor.
