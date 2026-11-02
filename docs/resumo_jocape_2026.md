# Proposta de projeto — XXVI JoCAPE 2026

**Título:** Plataforma digital de orientação às famílias de pessoas com deficiência sobre o atendimento odontológico no SUS: da integração de dados públicos com inteligência artificial ao cuidado resolutivo

**Autores:** Pedro Amaral; Francisco Perinni

O SUS garante atendimento odontológico às pessoas com deficiência, mas encontrar o serviço capaz de realizá-lo é um desafio para as famílias. Esse cuidado se organiza em níveis: unidades básicas, Centros de Especialidades Odontológicas (CEO) e atenção terciária, que inclui o tratamento hospitalar sob anestesia geral, indicado quando o paciente não pode ser atendido na cadeira odontológica. O caminho até o tratamento é marcado por tentativas, e as barreiras se somam: não saber onde procurar, não encontrar uma porta aberta ou chegar a um serviço que não realiza o procedimento necessário.

Um levantamento preliminar no município de São Paulo, que integrou dados públicos do CNES, do SIH/SUS e do Censo 2022 com apoio de inteligência artificial, dimensionou esse cenário. A cidade tem 719.261 pessoas com deficiência, das quais 42.329 são crianças de 2 a 14 anos, e 28 CEO com adesão à Rede de Cuidados à Pessoa com Deficiência, uma média de 25.688 pessoas com deficiência por centro. O tratamento sob anestesia geral foi realizado em 19 hospitais, mas 80% das 1.114 internações do último ano se concentraram em apenas 7 deles. A oferta resolutiva existe, mas é concentrada e pouco visível para as famílias.

O projeto propõe uma plataforma digital gratuita de prevenção e orientação aos pais e cuidadores. O responsável responde a perguntas simples, elaboradas por cirurgiões-dentistas da rede pública, sobre a necessidade do paciente. A plataforma indica o nível de atendimento adequado e os serviços mais próximos com maior chance de resolver o caso, considerando o perfil de cada unidade: procedimentos que de fato realiza, horários de funcionamento e volume de atendimento. Também explica o fluxo de encaminhamento no SUS e oferece conteúdos de cuidados bucais em casa. Um assistente com inteligência artificial responderá às dúvidas em linguagem simples, usando apenas informações validadas. A teleodontologia, na forma de teleorientação por cirurgiões-dentistas, funcionará como primeiro contato. A plataforma orienta, mas não substitui a avaliação presencial.

O desenvolvimento começará por São Paulo, com testes em casos simulados e, após aprovação em Comitê de Ética em Pesquisa, avaliação com famílias, em conformidade com a LGPD. Como as bases utilizadas são nacionais, o modelo poderá ser ampliado ao estado e replicado em qualquer município do país, a baixo custo. Mais do que mapear serviços, o projeto transforma dados públicos dispersos em orientação concreta, para que nenhuma família percorra a rede sem resposta e cada paciente chegue mais rápido ao tratamento de que precisa.

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
| 6 | Painel para gestores com as lacunas de oferta por território, atualizado automaticamente | Painel de apoio ao planejamento |
| 7 | Ampliação para a região metropolitana e depois para todo o estado, com atualização periódica automática das bases | Plataforma estadual |

**Cuidados éticos e legais:** Não coletar dados de saúde identificáveis dos pacientes (LGPD). Deixar claro que o cadastro de um serviço não garante vaga ou agenda. Registrar o uso de IA, com validação humana e trilha de auditoria.
