"""Coleta as habilitações do CNES para estabelecimentos candidatos do Estado de SP.

Fonte: serviço público da ficha de estabelecimento do CNES
(https://cnes.datasus.gov.br/services/estabelecimentos-habilitacoes/{CO_UNIDADE}).

Entrada: data/interim/sp_estab.csv (tbEstabelecimento filtrado para SP, ativos).
Saída:   data/raw/habilitacoes/{CO_UNIDADE}.json (cache, permite retomar)
         data/interim/habilitacoes_sp.csv (todas as habilitações coletadas)

Uso: python scripts/coletar_habilitacoes.py --competencia 202609
"""
import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "data/raw/habilitacoes"
URL = "https://cnes.datasus.gov.br/services/estabelecimentos-habilitacoes/{}?competencia={}"
FICHA = "https://cnes.datasus.gov.br/pages/estabelecimentos/ficha/index.jsp?coUnidade={}"

# Tipos de unidade em que CEOs costumam estar cadastrados (CNES TP_UNIDADE).
TIPOS = {"36", "02", "22", "04", "05", "39", "01", "15"}
PADRAO_NOME = r"\bCEO\b|C\.E\.O|ESPECIALIDADES? ODONT|ODONTOL"


def candidatos(sp: pd.DataFrame) -> pd.Series:
    """Unidades públicas/sem fins lucrativos dos tipos acima, mais qualquer nome sugestivo.

    Ordem de prioridade: nome sugestivo e público > público tipo 36 > demais.
    """
    publico = sp.CO_NATUREZA_JUR.fillna("").str.startswith(("1", "3"))
    tipo = sp.TP_UNIDADE.isin(TIPOS)
    nome = (sp.NO_FANTASIA.fillna("") + " " + sp.NO_RAZAO_SOCIAL.fillna("")).str.upper()
    sugestivo = nome.str.contains(PADRAO_NOME, regex=True)
    prioridade = (~(sugestivo & publico)).astype(int) + (~(publico & (sp.TP_UNIDADE == "36"))).astype(int)
    sel = sp.loc[(publico & tipo) | sugestivo].assign(p=prioridade)
    return sel.sort_values("p", kind="stable").CO_UNIDADE.drop_duplicates()


def buscar(co_unidade: str, competencia: str, sessao: requests.Session) -> None:
    destino = CACHE / f"{co_unidade}.json"
    if destino.exists():
        return
    for tentativa in range(4):
        try:
            r = sessao.get(
                URL.format(co_unidade, competencia),
                headers={"Referer": FICHA.format(co_unidade)},
                timeout=60,
            )
            if r.status_code == 200 and r.text.lstrip().startswith(("[", "{")):
                destino.write_text(r.text, encoding="utf-8")
                return
        except requests.RequestException:
            pass
        time.sleep(2 ** (tentativa + 1))
    print(f"falhou: {co_unidade}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--competencia", default="202609")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    sp = pd.read_csv(RAIZ / "data/interim/sp_estab.csv", dtype=str)
    ids = candidatos(sp).tolist()
    print(f"{len(ids)} estabelecimentos candidatos")

    sessao = requests.Session()
    with ThreadPoolExecutor(args.workers) as ex:
        for i, _ in enumerate(ex.map(lambda c: buscar(c, args.competencia, sessao), ids), 1):
            if i % 500 == 0:
                print(f"{i}/{len(ids)}")

    linhas = []
    for f in CACHE.glob("*.json"):
        for h in json.loads(f.read_text(encoding="utf-8")):
            linhas.append({"CO_UNIDADE": f.stem, **h})
    hab = pd.DataFrame(linhas)
    hab.to_csv(RAIZ / "data/interim/habilitacoes_sp.csv", index=False)
    print(f"{len(hab)} habilitações em {hab.CO_UNIDADE.nunique() if len(hab) else 0} unidades")


if __name__ == "__main__":
    main()
