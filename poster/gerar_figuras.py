"""Figuras do e-pôster (PP-06, XXVI JoCAPE): mapa do município de São Paulo e
concentração das internações odontológicas de pacientes com necessidades especiais.

Uso: python poster/gerar_figuras.py
Saída: poster/fig_mapa.png, poster/fig_concentracao.png
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

RAIZ = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
COD_SP = 355030

# Paleta do template da XXVI JoCAPE
TEAL, AMBAR, GRAFITE, CINZA, FUNDO = "#283888", "#E0A92E", "#1F2A30", "#B8C2C7", "#FFFFFF"
AZUL_CLARO = "#DCE8F1"
CM = 1 / 2.54
LARG_FIG = 6.94  # largura da coluna do pôster, em cm
plt.rcParams.update({"font.family": "Carlito", "font.size": 8, "text.color": GRAFITE,
                     "axes.labelcolor": GRAFITE, "xtick.color": GRAFITE, "ytick.color": GRAFITE})

# Nomes curtos para o gráfico (CNES -> rótulo)
NOMES = {
    "2069008": "AE Dr. Geraldo P. Bourroul",
    "6479200": "AME Dr. Luiz R. Barradas Barata",
    "2078015": "Hospital das Clínicas FMUSP",
    "2088495": "Inst. Dante Pazzanese",
    "2751976": "Hospital Dia São Miguel",
    "7378394": "Hospital Dia M'Boi Mirim II",
    "7979649": "Hospital Dia Vila Guilherme",
    "2066572": "Hospital Heliópolis",
    "2071371": "Hosp. Infantil Darcy Vargas",
    "2786680": "HM Fernando M. Pires da Rocha",
    "2081970": "HM Jabaquara",
    "2089696": "GRAACC",
    "2071568": "InCor",
    "2076926": "Hospital Universitário USP",
    "2082225": "HM Kátia de S. Rodrigues",
    "2077485": "Hospital São Paulo (Unifesp)",
    "2088517": "Hosp. Infantil Cândido Fontoura",
    "6123740": "ICESP",
    "9465464": "HM Josanias C. Braga",
}


# Coordenadas do CNES corrigidas após conferência do endereço (ViaCEP + OpenStreetMap);
# motivo de cada uma em data/processed/correcoes_coordenadas.csv.
_corr = pd.read_csv(RAIZ / "data/processed/correcoes_coordenadas.csv", dtype={"cnes": str})
CORRECOES = {r.cnes.zfill(7): (r.lat, r.lon) for r in _corr.itertuples()}


def poligonos_sp():
    geo = json.loads((RAIZ / "data/raw/ibge_malha_municipios_sp.geojson").read_text(encoding="utf-8"))
    for f in geo["features"]:
        if str(f["properties"].get("codarea", "")).startswith(str(COD_SP)):
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            return [p[0] for p in polys]
    raise ValueError("município não encontrado na malha")


FACULDADE, ONG = "#5E9CC4", "#A23B6B"


def mapa(ceo: pd.DataFrame, hosp: pd.DataFrame, extra: pd.DataFrame, nome="fig_mapa.png",
         larg=LARG_FIG, alt=7.3, fonte=8) -> None:
    """CEO (todos com atendimento a PNE), hospitais, faculdades e ONGs."""
    fig = plt.figure(figsize=(larg * CM, alt * CM), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1])
    for anel in poligonos_sp():
        ax.add_patch(Polygon(anel, closed=True, facecolor=AZUL_CLARO, edgecolor="#68A0C0", lw=0.8))
    k = fonte / 8
    ax.scatter(ceo.lon, ceo.lat, s=14 * k, marker="o", color=TEAL, edgecolor="white", lw=0.5, zorder=3)
    tam = (8 + hosp.internacoes * 0.55) * k
    top = hosp.internacoes >= hosp.internacoes.nlargest(7).min()
    ax.scatter(hosp[top].lon, hosp[top].lat, s=tam[top], marker="D", color=AMBAR,
               edgecolor="white", lw=0.5, alpha=0.95, zorder=4)
    ax.scatter(hosp[~top].lon, hosp[~top].lat, s=tam[~top], marker="D", color=CINZA,
               edgecolor="white", lw=0.8, alpha=0.95, zorder=4)
    fac, ong = extra[extra.tipo == "faculdade"], extra[extra.tipo == "ong"]
    ax.scatter(fac.lon, fac.lat, s=34 * k, marker="^", color=FACULDADE, edgecolor="white", lw=0.6, zorder=5)
    ax.scatter(ong.lon, ong.lat, s=50 * k, marker="*", color=ONG, edgecolor="white", lw=0.5, zorder=5)
    ax.set_aspect(1 / 0.917, adjustable="datalim")  # cos(23,6°)
    ax.autoscale_view()
    ax.axis("off")
    leg = [
        Line2D([], [], marker="o", ls="", color=TEAL, mec="white", ms=5 * k ** .5,
               label=f"CEO com atendimento\na PNE ({len(ceo)})"),
        Line2D([], [], marker="D", ls="", color=AMBAR, mec="white", ms=6 * k ** .5, label="7 hospitais com\n80% das internações"),
        Line2D([], [], marker="D", ls="", color=CINZA, mec="white", ms=4.5 * k ** .5, label="Outros 12 hospitais"),
        Line2D([], [], marker="^", ls="", color=FACULDADE, mec="white", ms=6 * k ** .5, label=f"Faculdades ({len(fac)})"),
        Line2D([], [], marker="*", ls="", color=ONG, mec="white", ms=8 * k ** .5, label=f"ONG ({len(ong)})"),
    ]
    ax.legend(handles=leg, loc="lower right", bbox_to_anchor=(1.0, 0.0), frameon=False, fontsize=fonte,
              handletextpad=0.3, labelspacing=0.35, borderaxespad=0)
    fig.savefig(OUT / nome, transparent=nome == "fig_mapa.png", facecolor="white")
    plt.close(fig)


def concentracao(hosp: pd.DataFrame) -> None:
    """Os 7 hospitais com mais internações, individualmente, e os demais somados."""
    h = hosp.sort_values("internacoes", ascending=False)
    top, resto = h.head(7).copy(), h.iloc[7:]
    top["rotulo"] = top.cnes.astype(str).str.zfill(7).map(NOMES)
    rot = list(top.rotulo) + [f"Outros {len(resto)} hospitais (soma)"]
    val = list(top.internacoes) + [int(resto.internacoes.sum())]
    cores = [AMBAR] * len(top) + [CINZA]
    fig, ax = plt.subplots(figsize=(LARG_FIG * CM, 3.8 * CM), dpi=400, layout="constrained")
    ys = list(range(len(rot)))[::-1]
    ax.barh(ys, val, color=cores, height=0.68)
    ax.set_yticks(ys, rot)
    for y, v in zip(ys, val):
        ax.text(v + 3, y, str(v), va="center", fontsize=8)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(CINZA)
    ax.tick_params(axis="y", length=0, labelsize=8, pad=2)
    ax.tick_params(axis="x", labelsize=8)
    ax.set_xlabel("Nº de internações", fontsize=8, labelpad=2)
    ax.set_xlim(0, max(val) * 1.18)
    fig.savefig(OUT / "fig_concentracao.png", transparent=True)
    plt.close(fig)


def main() -> None:
    ceo = pd.read_csv(RAIZ / "data/processed/ceo_sp.csv")
    ceo = ceo[ceo.co_ibge6 == COD_SP]
    hosp = pd.read_csv(RAIZ / "data/processed/hospitais_pne_sp.csv", dtype={"cnes": str})
    hosp = hosp[hosp.co_ibge6 == COD_SP].rename(columns={"NU_LATITUDE": "lat", "NU_LONGITUDE": "lon"})
    ceo = ceo.copy()
    for cnes, (lat, lon) in CORRECOES.items():
        ceo.loc[ceo.cnes.astype(str).str.zfill(7) == cnes, ["lat", "lon"]] = lat, lon
        hosp.loc[hosp.cnes.str.zfill(7) == cnes, ["lat", "lon"]] = lat, lon
    assert len(ceo) == 30 and ceo.adesao_rcpd.sum() == 28
    assert len(hosp) == 19 and hosp.internacoes.sum() == 1114
    assert hosp.internacoes.nlargest(7).sum() / hosp.internacoes.sum() >= 0.79
    # Lista da Prefeitura (out/2026): 31 CEO. O 31º (Itaim Paulista) não tem habilitação
    # de CEO no CNES; faculdades e ONGs vêm de fontes institucionais (nov/2026).
    extra = pd.read_csv(RAIZ / "data/processed/locais_complementares_sp.csv")
    ceo = pd.concat([ceo[["lat", "lon"]], extra.loc[extra.tipo == "ceo", ["lat", "lon"]]])
    assert len(ceo) == 31
    mapa(ceo, hosp, extra)
    mapa(ceo, hosp, extra, nome="mapa_servicos_pne_sp.png", larg=16, alt=17, fonte=12)
    concentracao(hosp)
    print("figuras geradas")


if __name__ == "__main__":
    main()
