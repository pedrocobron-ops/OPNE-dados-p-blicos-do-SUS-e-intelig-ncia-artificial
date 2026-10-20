"""Internações SUS para tratamento odontológico de pacientes com necessidades especiais.

Procedimento SIGTAP 0414020413 — TRATAMENTO ODONTOLOGICO PARA PACIENTES COM
NECESSIDADES ESPECIAIS (realizado em ambiente hospitalar, em geral sob anestesia
geral/sedação). Fonte: SIH/SUS via TabNet, "Procedimentos hospitalares do SUS -
por local de internação - São Paulo" (sih/cnv/qisp.def).

Diferente do CNES (cadastro), aqui é produção: internações aprovadas no período.

Saída: data/raw/sih_pne_{inicio}_{fim}.csv (estabelecimento × internações)
       data/processed/hospitais_pne_sp.csv (com município, endereço e coordenadas)

Uso: python scripts/coletar_sih_pne.py --meses 2509 2510 ... 2608
"""
import argparse
import html
import re
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
DEF = "sih/cnv/qisp.def"
URL = f"https://tabnet.datasus.gov.br/cgi/tabcgi.exe?{DEF}"
REFERER = f"https://tabnet.datasus.gov.br/cgi/deftohtm.exe?{DEF}"
OPCAO_PROCEDIMENTO = "3908"  # valor do <OPTION> para 0414020413 no formulário


def consultar(meses: list[str]) -> str:
    campos = [("Linha", "Estabelecimento"), ("Coluna", "--Não-Ativa--"),
              ("Incremento", "Internações")]
    campos += [("Arquivos", f"qisp{m}.dbf") for m in meses]
    campos += [("SMunicípio", "TODAS_AS_CATEGORIAS__"),
               ("SProcedimento", OPCAO_PROCEDIMENTO),
               ("formato", "prn"), ("mostre", "Mostra")]
    corpo = "&".join(f"{requests.utils.quote(k, encoding='latin1')}="
                     f"{requests.utils.quote(v, encoding='latin1')}" for k, v in campos)
    for tentativa in range(10):
        try:
            r = requests.post(URL, data=corpo, timeout=180, headers={
                "Referer": REFERER, "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/x-www-form-urlencoded"})
            if r.ok and "<PRE>" in r.text.upper():
                return r.content.decode("latin1")
        except requests.RequestException:
            pass
        time.sleep(3 * (tentativa + 1))
    raise RuntimeError("TabNet não respondeu")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meses", nargs="+", required=True, help="AAMM, ex.: 2509 2510")
    args = ap.parse_args()

    pagina = consultar(args.meses)
    pre = re.search(r"<PRE>(.*?)</PRE>", pagina, re.S | re.I).group(1)
    linhas = []
    for l in html.unescape(pre).splitlines():
        m = re.match(r'"(\d{7}) (.+)";(\d+)', l.strip())
        if m:
            linhas.append({"cnes": m[1], "nome_sih": m[2], "internacoes": int(m[3])})
    sih = pd.DataFrame(linhas)
    sih.to_csv(RAIZ / f"data/raw/sih_pne_{args.meses[0]}_{args.meses[-1]}.csv", index=False)

    sp = pd.read_csv(RAIZ / "data/interim/sp_estab.csv", dtype=str)
    est = sp[["CO_CNES", "CO_UNIDADE", "NO_FANTASIA", "NO_LOGRADOURO", "NU_ENDERECO",
              "NO_BAIRRO", "NU_TELEFONE", "NU_LATITUDE", "NU_LONGITUDE"]].rename(
        columns={"CO_CNES": "cnes"})
    out = sih.merge(est, how="left", on="cnes")
    out["co_ibge6"] = out.CO_UNIDADE.str[:6]
    out["periodo"] = f"{args.meses[0]}-{args.meses[-1]}"
    out.sort_values("internacoes", ascending=False).to_csv(
        RAIZ / "data/processed/hospitais_pne_sp.csv", index=False)
    print(f"{len(out)} hospitais, {out.internacoes.sum()} internações; "
          f"sem correspondência no CNES: {out.CO_UNIDADE.isna().sum()}")


if __name__ == "__main__":
    main()
