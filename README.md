# OPNE, dados públicos do SUS e inteligência artificial

Projeto XXVI JoCAPE 2026 — distribuição territorial dos Centros de Especialidades
Odontológicas (CEO) com atendimento à pessoa com deficiência no Estado de São Paulo.

## Fontes de dados

| Arquivo | Fonte | Conteúdo |
|---|---|---|
| `data/raw/ceoimp.csv.zip` | [Ministério da Saúde — dados abertos](https://dadosabertos.saude.gov.br/dataset/mgdi-rede-de-atencao-em-saude-bucal/resource/ceoimp_csv) | Nº de CEO implantados **por município** (agregado), dez/2019–jun/2026. Não identifica estabelecimentos nem adesão à RCPD. |
| `data/interim/sp_estab.csv` (não versionado) | [CNES — base de dados](https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp), competência 2026-09 | Estabelecimentos ativos de SP, com coordenadas. Gerado por `scripts/preparar_cnes.py`. |
| `data/interim/habilitacoes_sp.csv` | CNES — ficha do estabelecimento (`services/estabelecimentos-habilitacoes`) | Habilitações (CEO I/II/III etc.) dos estabelecimentos candidatos. Gerado por `scripts/coletar_habilitacoes.py`. |
| `data/raw/ibge_pop_censo2022_sp.json` | [IBGE/SIDRA tabela 4709](https://sidra.ibge.gov.br/tabela/4709) | População residente, Censo 2022, municípios de SP. |
| `data/raw/ibge_malha_municipios_sp.geojson` | [IBGE — API de malhas](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3) | Limites municipais de SP. |

| `data/interim/incentivos_ceo_sp.csv` | CNES — ficha do estabelecimento (`services/estabelecimentos-incentivo`) | Incentivos dos CEO. A adesão à RCPD está aqui (códigos 8231/8232/8233), não nas habilitações. |
| `data/processed/ceo_sp.csv` | Consolidação (`scripts/consolidar_ceo.py`) | Um registro por CEO habilitado: tipo, adesão à RCPD, endereço, coordenadas, município e região de saúde. |
| `data/processed/ceo_sp_municipios.csv` | Consolidação | Por município: população 2022, CEO segundo o MS e segundo o CNES, CEO com RCPD. |

Datas de extração: 20/10/2026.

## Reproduzir

```bash
pip install pandas requests
python scripts/preparar_cnes.py --competencia 202609
python scripts/coletar_habilitacoes.py --competencia 202609
python scripts/coletar_incentivos_ceo.py --competencia 202609
python scripts/consolidar_ceo.py
```

O servidor do CNES exige cabeçalho `Referer` e às vezes recusa conexões; o
coletor guarda cada resposta em `data/raw/habilitacoes/` e pode ser retomado.
