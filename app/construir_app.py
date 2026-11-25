"""Gera o protótipo do app (app/index.html) a partir do template e dos dados reais.

Embute no HTML: os 30 CEO e os 19 hospitais do município de São Paulo
(CNES 09/2026, SIH/SUS 09/2025-08/2026) e o contorno simplificado do município
(IBGE) para o mapa em SVG.

Uso: python app/construir_app.py
"""
import json
import re
from pathlib import Path

import pandas as pd
from shapely.geometry import Polygon

RAIZ = Path(__file__).resolve().parents[1]
AQUI = Path(__file__).resolve().parent
COD_SP = 355030
COD_SP7 = "3550308"
# Mesmas correções do pôster (data/processed/correcoes_coordenadas.csv).
_corr = pd.read_csv(RAIZ / "data/processed/correcoes_coordenadas.csv", dtype={"cnes": str})
CORRECOES = {r.cnes.zfill(7): (r.lat, r.lon) for r in _corr.itertuples()}

# Caixa de projeção do SVG (lon/lat -> x/y), com cos(lat) para manter proporção.
LON0, LON1, LAT0, LAT1 = -46.83, -46.36, -24.01, -23.35
ESCALA = 1000
COSLAT = 0.917

MINUSCULAS = {"de", "da", "do", "das", "dos", "e"}
SIGLAS = {"CEO", "II", "III", "I", "LRPD", "AME", "HC", "FMUSP", "USP", "HM", "SP", "UBS", "AE", "IOP",
          "GRAACC", "ICESP", "INCOR", "IDPC", "UGA", "UNIFESP", "DR", "M"}


def titulo(txt: str) -> str:
    palavras = []
    for i, p in enumerate(str(txt).split()):
        if p in SIGLAS:
            palavras.append({"DR": "Dr.", "INCOR": "InCor", "M": "M'"}.get(p, p))
        elif i and p.lower() in MINUSCULAS:
            palavras.append(p.lower())
        else:
            palavras.append(p.capitalize())
    return re.sub(r"M' (\w)", r"M'\1", " ".join(palavras))


def xy(lat: float, lon: float):
    x = (lon - LON0) * COSLAT * ESCALA
    y = (LAT1 - lat) * ESCALA
    return round(x, 1), round(y, 1)


def telefone(t) -> str:
    t = "" if pd.isna(t) else str(t).strip()
    return re.sub(r"\s+", " ", t)


def contorno() -> tuple[str, float, float]:
    geo = json.loads((RAIZ / "data/raw/ibge_malha_municipios_sp.geojson").read_text(encoding="utf-8"))
    f = next(f for f in geo["features"] if f["properties"]["codarea"] == COD_SP7)
    g = f["geometry"]
    aneis = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    caminhos = []
    for anel in aneis:
        poly = Polygon(anel[0]).simplify(0.002)
        pts = [xy(lat, lon) for lon, lat in poly.exterior.coords]
        caminhos.append("M" + " L".join(f"{x},{y}" for x, y in pts) + "Z")
    w = round((LON1 - LON0) * COSLAT * ESCALA)
    h = round((LAT1 - LAT0) * ESCALA)
    return " ".join(caminhos), w, h


def main() -> None:
    ceo = pd.read_csv(RAIZ / "data/processed/ceo_sp.csv", dtype={"cnes": str})
    ceo = ceo[ceo.co_ibge6 == COD_SP]
    hosp = pd.read_csv(RAIZ / "data/processed/hospitais_pne_sp.csv", dtype={"cnes": str})
    hosp = hosp[hosp.co_ibge6 == COD_SP].sort_values("internacoes", ascending=False)

    servicos = []
    for _, r in ceo.iterrows():
        cnes = r.cnes.zfill(7)
        lat, lon = CORRECOES.get(cnes, (r.lat, r.lon))
        x, y = xy(lat, lon)
        servicos.append({
            "id": cnes, "tipo": "ceo", "nome": titulo(r.nome), "porte": r.tipo_ceo,
            "rcpd": bool(r.adesao_rcpd),
            "endereco": f"{titulo(r.logradouro)}, {r.numero}" if not pd.isna(r.numero) else titulo(r.logradouro),
            "bairro": titulo(r.bairro), "telefone": telefone(r.telefone),
            "lat": round(lat, 5), "lon": round(lon, 5), "x": x, "y": y,
        })
    for _, r in hosp.iterrows():
        lat, lon = CORRECOES.get(r.cnes.zfill(7), (r.NU_LATITUDE, r.NU_LONGITUDE))
        x, y = xy(lat, lon)
        servicos.append({
            "id": r.cnes.zfill(7), "tipo": "hospital", "nome": titulo(r.NO_FANTASIA),
            "internacoes": int(r.internacoes),
            "endereco": f"{titulo(r.NO_LOGRADOURO)}, {r.NU_ENDERECO}",
            "bairro": titulo(r.NO_BAIRRO), "telefone": telefone(r.NU_TELEFONE),
            "lat": round(lat, 5), "lon": round(lon, 5), "x": x, "y": y,
        })
    # Lista da Prefeitura (out/2026): 31º CEO, faculdades e ONGs (fontes institucionais, nov/2026)
    extra = pd.read_csv(RAIZ / "data/processed/locais_complementares_sp.csv")
    for _, r in extra.iterrows():
        x, y = xy(r.lat, r.lon)
        servicos.append({
            "id": "x-" + str(len(servicos)), "tipo": r.tipo, "nome": r.nome,
            "porte": "CEO" if r.tipo == "ceo" else None, "rcpd": False,
            "endereco": r.endereco, "bairro": r.bairro, "telefone": r.telefone,
            "obs": r.observacao, "fonte": r.fonte,
            "lat": round(r.lat, 5), "lon": round(r.lon, 5), "x": x, "y": y,
        })
    assert sum(s["tipo"] == "ceo" for s in servicos) == 31
    assert sum(s["tipo"] == "hospital" for s in servicos) == 19

    caminho, w, h = contorno()
    html = (AQUI / "template.html").read_text(encoding="utf-8")
    html = (html.replace("__DADOS__", json.dumps(servicos, ensure_ascii=False))
                .replace("__CONTORNO__", caminho)
                .replace("__VIEWBOX__", f"0 0 {w} {h}"))
    (AQUI / "index.html").write_text(html, encoding="utf-8")
    print(f"app/index.html gerado ({len(html) // 1024} KB, {len(servicos)} serviços)")


if __name__ == "__main__":
    main()
