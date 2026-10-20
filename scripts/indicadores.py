"""Indicadores de oferta × população com deficiência, por município e região de saúde.

Não existe parâmetro oficial de "CEO com RCPD por pessoa com deficiência";
os indicadores são razões descritivas para comparar territórios.

Entradas: data/processed/{ceo_sp_municipios,hospitais_pne_sp}.csv,
          data/raw/ibge_deficiencia_sp.csv
Saídas:   data/processed/indicadores_municipios.csv
          data/processed/indicadores_regioes.csv

Uso: python scripts/indicadores.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PROC = RAIZ / "data/processed"
SOMAS = ["populacao_2022", "pcd_2mais", "pcd_2a14", "pcd_funcoes_mentais", "autismo",
         "autismo_0a14", "ceo_cnes", "ceo_rcpd", "hospitais_pne", "internacoes_pne"]


def razoes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rcpd = df.ceo_rcpd.where(df.ceo_rcpd > 0)
    df["pcd_por_ceo_rcpd"] = (df.pcd_2mais / rcpd).round(0)
    df["ceo_rcpd_por_100mil_pcd"] = (df.ceo_rcpd / df.pcd_2mais * 1e5).round(2)
    df["internacoes_pne_por_10mil_pcd"] = (df.internacoes_pne / df.pcd_2mais * 1e4).round(2)
    df["pct_pcd"] = (df.pcd_2mais / df.populacao_2022 * 100).round(1)
    return df


def main() -> None:
    mun = pd.read_csv(PROC / "ceo_sp_municipios.csv")
    ibge = pd.read_csv(RAIZ / "data/raw/ibge_deficiencia_sp.csv")
    hosp = pd.read_csv(PROC / "hospitais_pne_sp.csv")
    hosp = hosp.groupby("co_ibge6").agg(hospitais_pne=("cnes", "size"),
                                        internacoes_pne=("internacoes", "sum")).reset_index()

    mun = (mun.merge(ibge, on="co_ibge7", how="left")
              .merge(hosp, on="co_ibge6", how="left")
              .fillna({"hospitais_pne": 0, "internacoes_pne": 0}))
    mun = razoes(mun)
    mun.to_csv(PROC / "indicadores_municipios.csv", index=False)

    reg = mun.groupby(["co_regiao_saude", "no_regiao_saude"])[SOMAS].sum().reset_index()
    reg = razoes(reg).sort_values("pcd_por_ceo_rcpd", ascending=False, na_position="first")
    reg.to_csv(PROC / "indicadores_regioes.csv", index=False)

    est = mun[SOMAS].sum()
    print("ESTADO DE SP")
    print(f"  Pessoas com deficiência (2+ anos): {est.pcd_2mais:,.0f} "
          f"({est.pcd_2mais / est.populacao_2022:.1%} da população)")
    print(f"  ...limitação funções mentais: {est.pcd_funcoes_mentais:,.0f} | autismo: {est.autismo:,.0f} "
          f"| crianças 2-14 com deficiência: {est.pcd_2a14:,.0f}")
    print(f"  CEO: {est.ceo_cnes:.0f} | com RCPD: {est.ceo_rcpd:.0f} "
          f"-> {est.pcd_2mais / est.ceo_rcpd:,.0f} pessoas com deficiência por CEO-RCPD")
    print(f"  Internações odontológicas PNE (12 meses): {est.internacoes_pne:,.0f} "
          f"-> {est.internacoes_pne / est.pcd_2mais * 1e4:.1f} por 10 mil PcD")
    sem = reg[reg.ceo_rcpd == 0]
    print(f"  Regiões sem CEO-RCPD: {len(sem)} de {len(reg)}, com {sem.pcd_2mais.sum():,.0f} PcD "
          f"({sem.pcd_2mais.sum() / est.pcd_2mais:.0%})")
    semh = reg[reg.internacoes_pne == 0]
    print(f"  Regiões sem nenhuma internação PNE: {len(semh)}, com {semh.pcd_2mais.sum():,.0f} PcD")
    com = reg[reg.ceo_rcpd > 0].pcd_por_ceo_rcpd
    print(f"  PcD por CEO-RCPD entre regiões que têm: mín {com.min():,.0f} | "
          f"mediana {com.median():,.0f} | máx {com.max():,.0f}")
    cap = mun[mun.co_ibge6 == 355030].iloc[0]
    print(f"CAPITAL: {cap.pcd_2mais:,.0f} PcD, {cap.ceo_rcpd:.0f} CEO-RCPD -> "
          f"{cap.pcd_por_ceo_rcpd:,.0f} PcD por CEO-RCPD; {cap.internacoes_pne:.0f} internações PNE")


if __name__ == "__main__":
    main()
