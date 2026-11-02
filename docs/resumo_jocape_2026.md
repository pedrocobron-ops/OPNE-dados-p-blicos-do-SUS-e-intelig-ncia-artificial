# Resumo — XXVI JoCAPE 2026

**Título:** Oferta de atendimento odontológico especializado à pessoa com deficiência no município de São Paulo: mapeamento de dados públicos do SUS com apoio de inteligência artificial

**Autores:** Pedro Amaral; Francisco Perinni

No SUS, o atendimento odontológico às pessoas com deficiência se organiza em níveis de complexidade. Os Centros de Especialidades Odontológicas (CEO) com adesão à Rede de Cuidados à Pessoa com Deficiência (RCPD) atendem em ambulatório. Os pacientes que não podem ser tratados na cadeira odontológica precisam de tratamento hospitalar sob anestesia geral. Quando a família não sabe qual serviço resolve sua necessidade, pode percorrer locais que não realizam o procedimento indicado. Este estudo ecológico descritivo mapeou a oferta registrada e realizada desse atendimento no município de São Paulo e a relacionou à população com deficiência. É a etapa inicial de um mapeamento que será ampliado para todo o estado. Foram usadas três fontes públicas. Do Cadastro Nacional de Estabelecimentos de Saúde (CNES, competência 09/2026), vieram as habilitações de CEO e os incentivos de adesão à RCPD. Do Sistema de Informações Hospitalares (SIH/SUS, 09/2025 a 08/2026), vieram as internações pelo procedimento 0414020413, tratamento odontológico para pacientes com necessidades especiais. Do Censo Demográfico 2022, veio a população com deficiência. Ferramentas de automação e inteligência artificial apoiaram a coleta, a integração das bases e a identificação de inconsistências. A contagem de CEO foi conferida com a base oficial do Ministério da Saúde. O município tinha 30 CEO (2 do tipo I, 23 do tipo II e 5 do tipo III), número idêntico ao da base ministerial; 28 deles tinham adesão à RCPD. A cidade tem 719.261 pessoas com deficiência (6,3% da população de 2 anos ou mais), das quais 140.256 têm limitação nas funções mentais e 42.329 são crianças de 2 a 14 anos. Isso corresponde a 25.688 pessoas com deficiência por CEO com RCPD. No período, foram realizadas 1.114 internações para tratamento odontológico de pacientes com necessidades especiais em 19 hospitais da capital. A produção concentrou-se em 7 estabelecimentos, que somaram 80% das internações, enquanto 6 hospitais realizaram menos de 10 procedimentos no ano. Os resultados indicam que a oferta hospitalar, etapa decisiva para os casos mais complexos, depende de poucos serviços. O cadastro de um serviço não garante a disponibilidade do procedimento. A integração automatizada das bases mostrou-se viável, reprodutível e de baixo custo. Como plano de ação, essa base alimentará uma plataforma digital de auxílio aos pais. A partir de perguntas simples sobre a necessidade do paciente, a plataforma indicará o nível de atendimento adequado, os serviços disponíveis e o caminho de encaminhamento no SUS. Será validada por cirurgiões-dentistas e ampliada para todo o estado.

**Palavras-chave:** Pessoas com Deficiência; Assistência Odontológica; Sistemas de Informação em Saúde; Inteligência Artificial; Acesso aos Serviços de Saúde.

---

## Plano de ação — plataforma de auxílio aos pais

**Objetivo:** Ajudar pais e cuidadores de pessoas com deficiência a identificar, a partir da necessidade do paciente, o serviço odontológico do SUS capaz de resolvê-la, evitando deslocamentos a locais que não realizam o procedimento indicado.

**Como funciona:** O responsável informa o bairro ou município e responde a perguntas simples. Por exemplo: o paciente consegue ser atendido na cadeira odontológica? Já foi atendido em um CEO sem conclusão do tratamento? A plataforma indica o nível de atendimento adequado: unidade básica, CEO com adesão à RCPD ou tratamento hospitalar sob anestesia geral. Também mostra os serviços mais próximos daquele nível, com endereço, telefone e mapa, e explica o caminho de encaminhamento no SUS (o que solicitar e a quem). A plataforma orienta e não diagnostica: a indicação final é sempre do cirurgião-dentista.

**Papel da inteligência artificial:** Atualizar e integrar automaticamente as bases públicas (CNES, SIH/SUS e IBGE). Apontar inconsistências para revisão humana. Responder às dúvidas das famílias em linguagem simples, usando exclusivamente a base de serviços validada e citando a fonte e a data da informação.

**Etapas:**

| Etapa | Atividade | Entrega |
|---|---|---|
| 1 | Base de serviços do município de São Paulo, integrada e conferida com a base do Ministério da Saúde | Concluída |
| 2 | Definição, por cirurgiões-dentistas da rede pública, das perguntas de orientação e dos critérios de cada nível de atendimento | Regras de orientação validadas |
| 3 | Desenvolvimento do protótipo web, acessível e em linguagem simples, para o município de São Paulo | Protótipo funcional |
| 4 | Teste com casos simulados, cujas respostas são conferidas por cirurgiões-dentistas | Percentual de orientações corretas |
| 5 | Avaliação com famílias e profissionais, após aprovação em Comitê de Ética em Pesquisa | Avaliação de usabilidade e utilidade |
| 6 | Ampliação para a região metropolitana e depois para todo o estado, com atualização periódica automática das bases | Plataforma estadual |

**Cuidados éticos e legais:** Não coletar dados de saúde identificáveis dos pacientes (LGPD). Deixar claro que o cadastro de um serviço não garante vaga ou agenda. Registrar o uso de IA, com validação humana e trilha de auditoria.
