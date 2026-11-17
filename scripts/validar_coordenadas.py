"""Confere as coordenadas do CNES dos CEO e hospitais do município de São Paulo
contra a geocodificação do endereço (OpenStreetMap/Nominatim).

Diferenças acima de LIMITE_KM são registradas como inconsistências e a
coordenada geocodificada passa a ser usada no mapa.

Saída: data/processed/validacao_coordenadas_sp.csv
Uso: python scripts/validar_coordenadas.py
"""
import math
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
COD_SP = 355030
LIMITE_KM = 2.0
NOMINATIM = "https://nominatim.openstreetmap.org/search"


def distancia_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def geocodificar(logradouro: str, numero: str, sessao: requests.Session):
    rua = f"{numero} {logradouro}" if numero and numero.isdigit() else logradouro
    params = {"street": rua, "city": "São Paulo", "state": "SP", "country": "Brazil",
              "format": "json", "limit": 1}
    r = sessao.get(NOMINATIM, params=params, timeout=30,
                   headers={"User-Agent": "OPNE-projeto-pesquisa"})
    time.sleep(1.1)  # política de uso do Nominatim: 1 requisição/s
    js = r.json() if r.ok else []
    return (float(js[0]["lat"]), float(js[0]["lon"])) if js else (None, None)


def main() -> None:
    ceo = pd.read_csv(RAIZ / "data/processed/ceo_sp.csv", dtype={"cnes": str, "numero": str})
    ceo = ceo[ceo.co_ibge6 == COD_SP].assign(tipo="CEO")
    hosp = pd.read_csv(RAIZ / "data/processed/hospitais_pne_sp.csv", dtype={"cnes": str, "NU_ENDERECO": str})
    hosp = hosp[hosp.co_ibge6 == COD_SP].rename(columns={
        "nome_sih": "nome", "NO_LOGRADOURO": "logradouro", "NU_ENDERECO": "numero",
        "NU_LATITUDE": "lat", "NU_LONGITUDE": "lon"}).assign(tipo="Hospital")
    base = pd.concat([ceo[["tipo", "cnes", "nome", "logradouro", "numero", "lat", "lon"]],
                      hosp[["tipo", "cnes", "nome", "logradouro", "numero", "lat", "lon"]]])

    sessao = requests.Session()
    linhas = []
    for _, r in base.iterrows():
        glat, glon = geocodificar(str(r.logradouro), str(r.numero), sessao)
        d = distancia_km(r.lat, r.lon, glat, glon) if glat is not None else None
        linhas.append({**r.to_dict(), "lat_geo": glat, "lon_geo": glon,
                       "dist_km": None if d is None else round(d, 2),
                       "inconsistente": d is not None and d > LIMITE_KM})
    out = pd.DataFrame(linhas)
    out.to_csv(RAIZ / "data/processed/validacao_coordenadas_sp.csv", index=False)
    print(f"{len(out)} pontos | geocodificados: {out.lat_geo.notna().sum()} | "
          f"inconsistentes (> {LIMITE_KM} km): {out.inconsistente.sum()}")
    print(out[out.inconsistente][["tipo", "cnes", "nome", "dist_km"]].to_string(index=False))


if __name__ == "__main__":
    main()
