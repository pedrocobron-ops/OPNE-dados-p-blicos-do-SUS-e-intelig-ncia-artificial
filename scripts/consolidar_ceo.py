"""Consolida a base de CEO de SP: um registro por estabelecimento habilitado.

Entradas: data/interim/{sp_estab,habilitacoes_sp,incentivos_ceo_sp}.csv,
          data/raw/ceoimp.csv.zip, data/raw/ibge_pop_censo2022_sp.json
Saídas:   data/processed/ceo_sp.csv           (estabelecimentos)
          data/processed/ceo_sp_municipios.csv (municípios, comparação com o MS)

Uso: python scripts/consolidar_ceo.py
"""
import json
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
INTERIM = RAIZ / "data/interim"
OUT = RAIZ / "data/processed"
TIPO_CEO = {"0403": "CEO I", "0404": "CEO II", "0405": "CEO III"}
RCPD = {"8231", "8232", "8233"}
VIGENTE = "99/9999"


def main() -> None:
    sp = pd.read_csv(INTERIM / "sp_estab.csv", dtype=str)
    hab = pd.read_csv(INTERIM / "habilitacoes_sp.csv", dtype=str)
    inc = pd.read_csv(INTERIM / "incentivos_ceo_sp.csv", dtype=str)

    ceo = hab[hab.coGrupo.isin(TIPO_CEO) & (hab.dtCompFim == VIGENTE)].copy()
    ceo["tipo_ceo"] = ceo.coGrupo.map(TIPO_CEO)
    # Unidade com mais de uma habilitação de CEO vigente: fica a de maior porte.
    ceo = (ceo.sort_values("coGrupo")
              .groupby("CO_UNIDADE")
              .agg(tipo_ceo=("tipo_ceo", "last"),
                   n_habilitacoes_ceo=("coGrupo", "size"),
                   portaria_ceo=("portaria", "last"),
                   inicio_ceo=("dtCompInicio", "last"))
              .reset_index())

    rcpd = inc[inc.coGrupo.isin(RCPD) & (inc.dtCompFim == VIGENTE)]
    rcpd = rcpd.groupby("CO_UNIDADE").agg(
        rcpd_incentivo=("dsGrupo", "first"), rcpd_inicio=("dtCompInicio", "first"),
        rcpd_portaria=("portaria", "first")).reset_index()

    cols = {"CO_UNIDADE": "co_unidade", "CO_CNES": "cnes", "NO_FANTASIA": "nome",
            "NO_RAZAO_SOCIAL": "razao_social", "NO_LOGRADOURO": "logradouro",
            "NU_ENDERECO": "numero", "NO_BAIRRO": "bairro", "CO_CEP": "cep",
            "NU_TELEFONE": "telefone", "TP_UNIDADE": "tp_unidade",
            "CO_NATUREZA_JUR": "natureza_juridica", "NU_LATITUDE": "lat",
            "NU_LONGITUDE": "lon"}
    est = sp[list(cols)].rename(columns=cols)

    base = (ceo.rename(columns={"CO_UNIDADE": "co_unidade"})
               .merge(rcpd.rename(columns={"CO_UNIDADE": "co_unidade"}), how="left")
               .merge(est, how="left"))
    base["adesao_rcpd"] = base.rcpd_incentivo.notna()
    base["co_ibge6"] = base.co_unidade.str[:6].astype(int)

    # Municípios: nome, região de saúde e contagem oficial do MS (jun/2026)
    with zipfile.ZipFile(RAIZ / "data/raw/ceoimp.csv.zip") as z:
        ms = pd.read_csv(z.open("ceoimp.csv"))
    ms = ms[(ms.co_uf == 35) & (ms.co_anomes == ms.co_anomes.max())]
    mun = ms[["co_ibge", "no_municipio", "co_regiao_saude", "no_regiao_saude",
              "vl_indicador_calculado_mun"]].rename(
        columns={"co_ibge": "co_ibge6", "vl_indicador_calculado_mun": "ceo_ms"})

    pop = json.loads((RAIZ / "data/raw/ibge_pop_censo2022_sp.json").read_text(encoding="utf-8"))[1:]
    pop = pd.DataFrame({"co_ibge7": [p["D1C"] for p in pop],
                        "populacao_2022": [int(p["V"]) for p in pop]})
    pop["co_ibge6"] = pop.co_ibge7.str[:6].astype(int)
    mun = mun.merge(pop, how="left")

    base = base.merge(mun[["co_ibge6", "co_ibge7", "no_municipio", "co_regiao_saude",
                           "no_regiao_saude"]], how="left")

    cont = base.groupby("co_ibge6").agg(ceo_cnes=("co_unidade", "size"),
                                        ceo_rcpd=("adesao_rcpd", "sum")).reset_index()
    mun = mun.merge(cont, how="left").fillna({"ceo_cnes": 0, "ceo_rcpd": 0})
    mun[["ceo_cnes", "ceo_rcpd"]] = mun[["ceo_cnes", "ceo_rcpd"]].astype(int)
    mun["diverge_ms_cnes"] = mun.ceo_ms != mun.ceo_cnes

    OUT.mkdir(parents=True, exist_ok=True)
    base.to_csv(OUT / "ceo_sp.csv", index=False)
    mun.to_csv(OUT / "ceo_sp_municipios.csv", index=False)

    print(f"CEO no CNES: {len(base)} ({base.tipo_ceo.value_counts().to_dict()})")
    print(f"Com adesão à RCPD: {base.adesao_rcpd.sum()}")
    print(f"Municípios com CEO: CNES {(mun.ceo_cnes > 0).sum()} | MS {(mun.ceo_ms > 0).sum()}")
    print(f"Total MS (jun/2026): {int(mun.ceo_ms.sum())}")
    print("Divergências MS × CNES:")
    print(mun[mun.diverge_ms_cnes][["no_municipio", "ceo_ms", "ceo_cnes"]].to_string(index=False))
    dup = base[base.n_habilitacoes_ceo > 1]
    if len(dup):
        print("Unidades com mais de uma habilitação de CEO vigente:")
        print(dup[["cnes", "nome", "no_municipio"]].to_string(index=False))


if __name__ == "__main__":
    main()
