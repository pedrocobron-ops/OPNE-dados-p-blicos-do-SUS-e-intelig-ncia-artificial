"""Coleta os incentivos do CNES dos estabelecimentos habilitados como CEO.

A adesão do CEO à Rede de Cuidados à Pessoa com Deficiência (RCPD) não é uma
habilitação: aparece na aba "Incentivos" da ficha do CNES, códigos 8231/8232/8233
(CEO-I/II/III - Rede de Cuidados à Pessoa com Deficiência).

Entrada: data/raw/habilitacoes/*.json (de coletar_habilitacoes.py)
Saída:   data/raw/incentivos/{CO_UNIDADE}.json
         data/interim/incentivos_ceo_sp.csv

Uso: python scripts/coletar_incentivos_ceo.py --competencia 202609
"""
import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
HAB = RAIZ / "data/raw/habilitacoes"
CACHE = RAIZ / "data/raw/incentivos"
URL = "https://cnes.datasus.gov.br/services/estabelecimentos-incentivo/{}?competencia={}"
FICHA = "https://cnes.datasus.gov.br/pages/estabelecimentos/ficha/index.jsp?coUnidade={}"
CEO = {"0403", "0404", "0405"}


def unidades_ceo() -> list[str]:
    return sorted(
        f.stem for f in HAB.glob("*.json")
        if any(h["coGrupo"] in CEO for h in json.loads(f.read_text(encoding="utf-8")))
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--competencia", default="202609")
    args = ap.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    sessao = requests.Session()
    ids = unidades_ceo()
    for co in ids:
        destino = CACHE / f"{co}.json"
        if destino.exists():
            continue
        for tentativa in range(4):
            try:
                r = sessao.get(URL.format(co, args.competencia),
                               headers={"Referer": FICHA.format(co)}, timeout=60)
                if r.status_code == 200 and r.text.lstrip().startswith(("[", "{")):
                    destino.write_text(r.text, encoding="utf-8")
                    break
            except requests.RequestException:
                pass
            time.sleep(2 ** (tentativa + 1))
        else:
            print(f"falhou: {co}")

    linhas = [
        {"CO_UNIDADE": f.stem, **i}
        for f in CACHE.glob("*.json")
        for i in json.loads(f.read_text(encoding="utf-8"))
    ]
    pd.DataFrame(linhas).to_csv(RAIZ / "data/interim/incentivos_ceo_sp.csv", index=False)
    print(f"{len(ids)} CEO consultados, {len(linhas)} incentivos")


if __name__ == "__main__":
    main()
