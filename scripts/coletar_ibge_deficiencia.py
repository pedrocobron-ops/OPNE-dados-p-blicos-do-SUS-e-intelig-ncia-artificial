"""Pessoas com deficiência e com autismo por município de SP — Censo 2022 (IBGE).

Tabelas SIDRA:
- 10125: pessoas de 2+ anos, total e com deficiência, por grupo de idade
- 10127: pessoas de 2+ anos com deficiência por tipo de dificuldade funcional
         (73790 = limitação nas funções mentais: comunicar, cuidar de si, estudar)
- 10145: população total e diagnosticada com autismo, por grupo de idade

Saída: data/raw/ibge_deficiencia_sp.csv (um registro por município)

Uso: python scripts/coletar_ibge_deficiencia.py
"""
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
API = "https://servicodados.ibge.gov.br/api/v3/agregados/{t}/periodos/2022/variaveis/{v}?localidades=N6[N3[35]]&classificacao={c}"

CONSULTAS = {
    "pcd_2mais": (10125, 12785, "58[95253]|2[6794]"),
    "pcd_2a14": (10125, 12785, "58[73770]|2[6794]"),
    "pop_2mais": (10125, 11852, "58[95253]|2[6794]"),
    "pop_2a14": (10125, 11852, "58[73770]|2[6794]"),
    "pcd_funcoes_mentais": (10127, 12785, "1509[73790]"),
    "autismo": (10145, 13267, "58[95253]|2[6794]"),
    "autismo_0a4": (10145, 13267, "58[1140]|2[6794]"),
    "autismo_5a9": (10145, 13267, "58[1141]|2[6794]"),
    "autismo_10a14": (10145, 13267, "58[1142]|2[6794]"),
}


def buscar(t: int, v: int, c: str) -> pd.Series:
    for tentativa in range(5):
        try:
            r = requests.get(API.format(t=t, v=v, c=c), timeout=120)
            r.raise_for_status()
            series = r.json()[0]["resultados"][0]["series"]
            return pd.Series({s["localidade"]["id"]: s["serie"]["2022"] for s in series})
        except (requests.RequestException, KeyError, IndexError):
            time.sleep(3 * (tentativa + 1))
    raise RuntimeError(f"falha na tabela {t}")


def main() -> None:
    df = pd.DataFrame({nome: buscar(*args) for nome, args in CONSULTAS.items()})
    # "-" e "X" no SIDRA = zero / sigilo
    df = df.apply(pd.to_numeric, errors="coerce")
    df["autismo_0a14"] = df[["autismo_0a4", "autismo_5a9", "autismo_10a14"]].sum(axis=1, min_count=1)
    df.index.name = "co_ibge7"
    df.reset_index().to_csv(RAIZ / "data/raw/ibge_deficiencia_sp.csv", index=False)
    print(f"{len(df)} municípios")
    print(df.sum(numeric_only=True).astype("int64").to_string())


if __name__ == "__main__":
    main()
