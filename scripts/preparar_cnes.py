"""Baixa a base de dados do CNES e extrai os estabelecimentos ativos de SP.

Fonte: https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp
O ZIP é grande (>300 MB) e o servidor costuma cortar a conexão antes do fim.
Como o arquivo é gravado em fluxo (entradas com data descriptor), as tabelas
que chegaram completas podem ser extraídas mesmo sem o diretório central do ZIP.
tbEstabelecimento é a segunda entrada e chega nos primeiros ~100 MB.

Saída: data/interim/sp_estab.csv

Uso: python scripts/preparar_cnes.py --competencia 202609
"""
import argparse
import struct
import subprocess
import zlib
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
URL = "https://cnes.datasus.gov.br/EstatisticasServlet?path=BASE_DE_DADOS_CNES_{}.ZIP"
REFERER = "https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp"


def extrair_entrada(zip_parcial: Path, nome: str, destino: Path) -> None:
    """Descomprime uma entrada (deflate) procurando o cabeçalho local pelo nome."""
    dados = zip_parcial.read_bytes()
    i = 0
    while (i := dados.find(b"PK\x03\x04", i)) >= 0:
        h = struct.unpack("<HHHHHIIIHH", dados[i + 4:i + 30])
        n_nome, n_extra = h[8], h[9]
        if dados[i + 30:i + 30 + n_nome].decode("latin1") == nome:
            d = zlib.decompressobj(-15)
            pos = i + 30 + n_nome + n_extra
            with destino.open("wb") as out:
                while not d.eof and pos < len(dados):
                    out.write(d.decompress(dados[pos:pos + (1 << 20)]))
                    pos += 1 << 20
            if not d.eof:
                raise RuntimeError(f"{nome} incompleto no download")
            return
        i += 30
    raise FileNotFoundError(nome)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--competencia", default="202609")
    args = ap.parse_args()

    raw = RAIZ / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    zip_path = raw / f"BASE_DE_DADOS_CNES_{args.competencia}.ZIP"
    if not zip_path.exists():
        # curl devolve erro quando o servidor corta a conexão; o parcial basta.
        subprocess.run(["curl", "-sS", "-H", f"Referer: {REFERER}", "-o", str(zip_path),
                        URL.format(args.competencia)])

    csv = raw / f"tbEstabelecimento{args.competencia}.csv"
    if not csv.exists():
        extrair_entrada(zip_path, csv.name, csv)

    d = pd.read_csv(csv, sep=";", dtype=str, encoding="latin1")
    d.columns = [c.replace("TO_CHAR(", "").split(",")[0] for c in d.columns]
    sp = d[d.CO_UNIDADE.str.startswith("35") & d.CO_MOTIVO_DESAB.isna()]
    (RAIZ / "data/interim").mkdir(parents=True, exist_ok=True)
    sp.to_csv(RAIZ / "data/interim/sp_estab.csv", index=False)
    print(f"{len(sp)} estabelecimentos ativos em SP")


if __name__ == "__main__":
    main()
