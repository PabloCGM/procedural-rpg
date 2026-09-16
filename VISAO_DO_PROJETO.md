# Procedural RPG — visão consolidada

Síntese das definições atuais. Detalhes e propostas técnicas estão em `IDEIA.md`. Este documento não é a especificação final da E2.

## Propósito

Criar uma linguagem de domínio específico para uma IA construir e desenvolver campanhas de RPG coerentes, a partir de um universo persistente. O foco é a narrativa, independente de um sistema específico de regras.

## Organização

A linguagem será orientada a objetos, com entidades dotadas de identidade, atributos e métodos. O operador `.` acessará membros; a criação deverá explicitar o objeto proprietário, como na proposta `universo.personagem("helena")`. Criação e acesso a objetos existentes serão operações distintas. Blocos usarão indentação obrigatória, sem `fim`. Sintaxe detalhada, encapsulamento e recursos de classes permanecem em definição.

**Composição proposta: universo → campanhas → histórias → capítulos → cenas.** Marcos pertencem diretamente à história e formam uma rede transversal de progresso, referenciada pelos capítulos e cenas.

Cada nível contém o seguinte. Cenários e personagens compõem o contexto das cenas. Permanecem no modelo também estado, jogador/ficha, itens e inventário. As outras sugestões de entidades e os moldes arbitrários ficam suspensos.

- **Universo:** identidade, fatos, contexto e estado compartilhado do mundo.
- **Campanha:** continuidade dos personagens dos jogadores, seus únicos personagens próprios, podendo conter várias histórias.
- **História:** fio condutor planejado, com objetivo e percurso até seu encerramento.
- **Capítulos:** organização narrativa; podem definir ou referenciar NPCs.
- **Marcos:** checkpoints conectados no escopo da história; controlam progresso independentemente da divisão em capítulos e não criam personagens.
- **Cenas:** situações geradas durante o jogo usando o contexto pertinente.

O universo é definido primeiro. Depois se cria a campanha, seus personagens e a primeira história, considerando universo e personagens. Outras histórias mantêm a continuidade desse grupo; outra campanha começa com novos personagens de jogador.

NPCs podem ser definidos no universo, história, capítulo ou cena e participar de outros contextos por referência. Cada personagem possui uma única identidade e definição. Ser recorrente não torna um NPC pertencente à campanha. Histórias e capítulos guardam seu papel planejado; cenas registram sua participação; o estado guarda mudanças efetivamente ocorridas.

Os marcos devem refletir avanços da história, sem exigir uma cena ou capítulo específico. Dependências e critérios de conclusão ainda serão definidos. A intenção é permitir diferentes caminhos coerentes e reduzir direcionamentos artificiais impostos pelo planejamento de cada capítulo.

## Base sólida e geração

Identidade, características, relações e informações necessárias das entidades são pré-geradas e persistidas, assim como o esboço da história, capítulos e marcos. A IA desenvolve cenas e preenche os espaços narrativos livres respeitando essa base.

Fatos estabelecidos não devem ser reinventados. Mudanças causadas pela história são permitidas e precisam ser registradas. O procedimento para incorporar novos detalhes ao conjunto de fatos estabelecidos ainda será definido.

## Criação e consulta

A IA acessará funções com procedimentos de criação: contexto necessário, informações obrigatórias e requisitos de conclusão. A proposta é gerar, validar e salvar cada entidade antes de seu uso, evitando definições incompletas que dependam de improvisações posteriores.

Entidades e subentidades têm organização lógica hierárquica e referências entre si. A própria linguagem poderá expressar essas relações, inclusive por caminhos qualificados. A árvore de pastas inicialmente proposta é uma alternativa de armazenamento; arquivos ou banco de dados poderão manter a fonte de verdade. A IA consultará o contexto pertinente, sem depender exclusivamente da memória da conversa.

Personagens compartilhados terão uma definição canônica, referenciada nos contextos narrativos. Formatos de armazenamento, resolução de nomes e regras de visibilidade não estão fechados. NPCs incidentais podem ser criados durante a campanha, desde que definidos antes de seu uso; campos obrigatórios e promoção de escopo ainda serão especificados.

## Estados e continuidade

O universo é o guardião conceitual de seu estado. Campanhas podem ter estado próprio, mas alterações de alcance global devem refletir no universo e ser consideradas quando pertinentes às demais campanhas.

Quem valida e aplica essas mudanças, a cronologia e os conflitos entre campanhas permanecem em aberto. A base sólida limita reinterpretações, mas não impede a evolução do mundo.

## Limite acadêmico

Na E2: especificação de um recorte pequeno, lexer ANTLR, listagem de tokens e erros, três exemplos válidos e três inválidos, documentação e diário. E3 trata da sintaxe; E4, da semântica e execução.

A visão completa não é compromisso de entrega na E2. Ainda precisamos escolher o recorte, atributos, sintaxe, operações e três exclusões explícitas da linguagem. Integração com IA e persistência completa são construções posteriores.
