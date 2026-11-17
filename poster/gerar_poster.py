"""Monta o e-pôster PP-06 (XXVI JoCAPE) sobre o template oficial.

Normas: slide único retrato 15,752 × 28,002 cm; Arial ou Calibri; título ≥ 16 pt,
conteúdo ≥ 8 pt; número do pôster no canto superior esquerdo; título em inglês
idêntico ao do resumo; corpo em português.

Uso: python poster/gerar_figuras.py && python poster/gerar_poster.py
Saída: poster/PP-06_JoCAPE_2026.pptx
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Cm, Pt

AQUI = Path(__file__).resolve().parent
TEMPLATE = AQUI / "TEMPLATE_XXVI_JOCAPE.pptx"
SAIDA = AQUI / "PP-06_JoCAPE_2026.pptx"

FONTE = "Calibri"
MARINHO = RGBColor(0x28, 0x38, 0x88)
AZUL = RGBColor(0x68, 0xA0, 0xC0)
AMARELO = RGBColor(0xE8, 0xC8, 0x58)
AZUL_CLARO = RGBColor(0xDC, 0xE8, 0xF1)
TEXTO = RGBColor(0x1F, 0x2A, 0x30)

CODIGO = "PP-06"
TITULO = ("ACCESS TO SPECIALIZED DENTAL CARE FOR PERSONS WITH DISABILITIES IN SÃO PAULO: "
          "PUBLIC DATA AND ARTIFICIAL INTELLIGENCE")
# Preencher antes do envio
AUTORES = [("Francisco Perinni", "1"), ("Pedro Amaral", "2"), ("[Nome da orientadora]", "3")]
AFILIACOES = "¹[Instituição, Cidade – UF].  ²[Instituição, Cidade – UF].  ³[Instituição, Cidade – UF]."
EMAIL = "[e-mail do autor principal]"

MARGEM = 0.74
LARGURA = 15.752 - 2 * MARGEM
COL = (LARGURA - 0.4) / 2
X1, X2 = MARGEM, MARGEM + COL + 0.4


def caixa(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def run(par, texto, tam=8.5, negrito=False, cor=TEXTO, italico=False, sobrescrito=False):
    r = par.add_run()
    r.text = texto
    f = r.font
    f.name, f.size, f.bold, f.italic = FONTE, Pt(tam), negrito, italico
    f.color.rgb = cor
    if sobrescrito:
        r._r.get_or_add_rPr().set("baseline", "30000")
    return r


def paragrafo(tf, primeiro=False, alinhar=PP_ALIGN.LEFT, depois=2):
    p = tf.paragraphs[0] if primeiro else tf.add_paragraph()
    p.alignment = alinhar
    p.space_after = Pt(depois)
    p.line_spacing = 1.0
    return p


def secao(slide, x, y, w, titulo):
    """Título de seção com barra amarela à esquerda. Retorna o y seguinte."""
    barra = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(x), Cm(y + 0.05), Cm(0.12), Cm(0.42))
    barra.fill.solid()
    barra.fill.fore_color.rgb = AMARELO
    barra.line.fill.background()
    tf = caixa(slide, x + 0.25, y, w - 0.25, 0.5)
    run(paragrafo(tf, True, PP_ALIGN.LEFT), titulo, 10.5, True, MARINHO)
    return y + 0.55


def texto(slide, x, y, w, h, blocos):
    """blocos: lista de parágrafos; cada parágrafo é lista de (texto, kwargs)."""
    tf = caixa(slide, x, y, w, h)
    for i, partes in enumerate(blocos):
        p = paragrafo(tf, i == 0)
        for t, kw in partes:
            run(p, t, **kw)
    return y + h


def retangulo(slide, x, y, w, h, cor, arredondado=True):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if arredondado else MSO_SHAPE.RECTANGLE,
                               Cm(x), Cm(y), Cm(w), Cm(h))
    if arredondado:
        s.adjustments[0] = 0.12
    s.fill.solid()
    s.fill.fore_color.rgb = cor
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def indicador(slide, x, y, w, h, numero, rotulo):
    retangulo(slide, x, y, w, h, AZUL_CLARO)
    tf = caixa(slide, x + 0.15, y + 0.12, w - 0.3, h - 0.2)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    run(paragrafo(tf, True, PP_ALIGN.CENTER, 0), numero, 15, True, MARINHO)
    run(paragrafo(tf, False, PP_ALIGN.CENTER, 0), rotulo, 8, False, TEXTO)


def etapa(slide, x, y, w, h, n, titulo, detalhe):
    retangulo(slide, x, y, w, h, MARINHO)
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, Cm(x + 0.18), Cm(y + (h - 0.62) / 2), Cm(0.62), Cm(0.62))
    circ.fill.solid()
    circ.fill.fore_color.rgb = AMARELO
    circ.line.fill.background()
    ctf = circ.text_frame
    ctf.margin_left = ctf.margin_right = ctf.margin_top = ctf.margin_bottom = 0
    ctf.vertical_anchor = MSO_ANCHOR.MIDDLE
    run(paragrafo(ctf, True, PP_ALIGN.CENTER, 0), str(n), 9, True, MARINHO)
    tf = caixa(slide, x + 0.95, y + 0.08, w - 1.1, h - 0.16)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    run(paragrafo(tf, True, PP_ALIGN.LEFT, 0), titulo, 8.5, True, RGBColor(0xFF, 0xFF, 0xFF))
    run(paragrafo(tf, False, PP_ALIGN.LEFT, 0), detalhe, 8, False, RGBColor(0xE6, 0xEC, 0xF5))


def seta(slide, x, y1, y2):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x), Cm(y1), Cm(x), Cm(y2))
    c.line.color.rgb = AZUL
    c.line.width = Pt(1.5)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd",
                             {"type": "triangle", "w": "med", "len": "med"}))


def cabecalho(slide):
    for sh in list(slide.shapes):
        if sh.has_text_frame and sh.text_frame.text.startswith("[Código"):
            sh.text_frame.paragraphs[0].runs[0].text = CODIGO
            sh.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
            sh.text_frame.paragraphs[0].runs[0].font.color.rgb = MARINHO
        elif sh.has_text_frame and sh.text_frame.text.startswith("Título"):
            sh.left, sh.top, sh.width, sh.height = Cm(0.5), Cm(1.55), Cm(9.7), Cm(2.3)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.paragraphs[0].runs[0].text = TITULO
            for r in tf.paragraphs[0].runs[1:]:
                r.text = ""
        elif sh.has_text_frame and sh.text_frame.text.startswith("Autor"):
            sh.left, sh.top, sh.width, sh.height = Cm(0.5), Cm(3.95), Cm(14.5), Cm(1.2)
            tf = sh.text_frame
            for p in list(tf.paragraphs)[1:]:
                p._p.getparent().remove(p._p)
            p = tf.paragraphs[0]
            for r in list(p.runs):
                r._r.getparent().remove(r._r)
            p.alignment = PP_ALIGN.LEFT
            for i, (nome, sup) in enumerate(AUTORES):
                run(p, nome, 8.5, i == 0)
                run(p, sup + ("*" if i == 0 else ""), 8.5, i == 0, sobrescrito=True)
                run(p, "; " if i < len(AUTORES) - 1 else ".", 8.5)
            run(paragrafo(tf, False, PP_ALIGN.LEFT, 0), AFILIACOES, 8)
            p = paragrafo(tf, False, PP_ALIGN.LEFT, 0)
            run(p, "*Autor apresentador. E-mail para contato: ", 8)
            run(p, EMAIL, 8, cor=MARINHO)
        elif sh.name in ("Retângulo 37", "Retângulo 40"):
            sh._element.getparent().remove(sh._element)
    linha = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(MARGEM), Cm(5.3), Cm(15.752 - MARGEM), Cm(5.3))
    linha.line.color.rgb = AZUL
    linha.line.width = Pt(1)


def coluna_esquerda(slide):
    y = 5.6
    y = secao(slide, X1, y, COL, "INTRODUÇÃO")
    y = texto(slide, X1, y, COL, 2.25, [[
        ("Embora o SUS garanta atendimento odontológico às pessoas com deficiência (PcD), o acesso "
         "aos serviços adequados ainda é um desafio. As famílias frequentemente têm dificuldade para "
         "identificar os serviços e percorrer os fluxos de encaminhamento entre a atenção primária, "
         "secundária e terciária.", {})]]) + 0.15

    y = secao(slide, X1, y, COL, "OBJETIVO")
    y = texto(slide, X1, y, COL, 1.6, [[
        ("Desenvolver uma plataforma digital gratuita que integre dados públicos de saúde, "
         "teleconsulta e inteligência artificial (IA) para orientar famílias de PcD ao "
         "atendimento odontológico adequado no SUS.", {})]]) + 0.15

    y = secao(slide, X1, y, COL, "METODOLOGIA")
    y = texto(slide, X1, y, COL, 4.5, [
        [("Levantamento preliminar no município de São Paulo, com apoio de IA na coleta, "
          "integração e detecção de inconsistências, em três bases públicas:", {})],
        [("• CNES ", {"negrito": True}), ("(09/2026): Centros de Especialidades Odontológicas (CEO) "
          "e adesão à Rede de Cuidados à Pessoa com Deficiência (RCPD);", {})],
        [("• SIH/SUS ", {"negrito": True}), ("(09/2025 a 08/2026): internações pelo procedimento "
          "04.14.02.041-3, tratamento odontológico para pacientes com necessidades especiais;", {})],
        [("• Censo 2022 ", {"negrito": True}), ("(IBGE): população com deficiência.", {})],
        [("A contagem de CEO foi conferida com a base do Ministério da Saúde.", {})],
    ]) + 0.1

    y = secao(slide, X1, y, COL, "PLATAFORMA PROPOSTA")
    h, gap = 0.9, 0.2
    etapas = [
        ("Questionário do cuidador", "Necessidade do paciente em linguagem simples"),
        ("Teleconsulta", "Com cirurgiões-dentistas cadastrados"),
        ("Diretório georreferenciado", "Serviço e encaminhamento adequados no SUS"),
    ]
    for i, (t, d) in enumerate(etapas, 1):
        etapa(slide, X1, y, COL, h, i, t, d)
        if i < len(etapas):
            seta(slide, X1 + COL / 2, y + h + 0.02, y + h + gap - 0.02)
        y += h + gap
    y -= gap - 0.2
    retangulo(slide, X1, y, COL, 2.45, AZUL_CLARO)
    texto(slide, X1 + 0.22, y + 0.13, COL - 0.44, 2.15, [
        [("Transversal: ", {"negrito": True, "cor": MARINHO}),
         ("educação em saúde bucal e assistente de IA com respostas baseadas em evidências.", {})],
        [("Próximas etapas: ", {"negrito": True, "cor": MARINHO}),
         ("início em São Paulo, testes com casos simulados e, após aprovação do Comitê de Ética "
          "em Pesquisa, avaliação com famílias, em conformidade com a LGPD.", {})],
    ])


def coluna_direita(slide):
    y = 5.6
    y = secao(slide, X2, y, COL, "RESULTADOS")
    w2 = (COL - 0.2) / 2
    hk = 1.15
    indicador(slide, X2, y, w2, hk, "719.261", "pessoas com deficiência")
    indicador(slide, X2 + w2 + 0.2, y, w2, hk, "42.329", "crianças de 2 a 14 anos")
    y += hk + 0.2
    indicador(slide, X2, y, w2, hk, "28", "CEO com adesão à RCPD")
    indicador(slide, X2 + w2 + 0.2, y, w2, hk, "25.688", "PcD por CEO da RCPD")
    y += hk + 0.25

    tf = caixa(slide, X2, y, COL, 0.4)
    run(paragrafo(tf, True, PP_ALIGN.LEFT, 0), "Figura 1. Localização dos CEO e dos hospitais",
        8, True, MARINHO)
    y += 0.4
    slide.shapes.add_picture(str(AQUI / "fig_mapa.png"), Cm(X2), Cm(y), width=Cm(COL))
    y += 6.9 + 0.2

    tf = caixa(slide, X2, y, COL, 0.8)
    p = paragrafo(tf, True, PP_ALIGN.LEFT, 0)
    run(p, "Figura 2. ", 8, True, MARINHO)
    run(p, "Internações para tratamento odontológico sob anestesia geral: 7 de 19 hospitais concentraram ", 8, True, MARINHO)
    run(p, "80% das 1.114 internações", 8, True, RGBColor(0xB0, 0x7A, 0x10))
    y += 0.8
    slide.shapes.add_picture(str(AQUI / "fig_concentracao.png"), Cm(X2), Cm(y), width=Cm(COL))



def conclusoes(slide, y):
    y = secao(slide, X1, y, LARGURA, "CONCLUSÕES")
    y = texto(slide, X1, y, LARGURA, 1.45, [[
        ("A rede de atendimento odontológico especializado às PcD em São Paulo é altamente concentrada. "
         "A plataforma transformará dados públicos fragmentados em orientação acessível, ajudando as "
         "famílias a identificar serviços e fluxos de encaminhamento adequados. Por usar bases de "
         "abrangência nacional, o modelo pode ser expandido ao estado e replicado no Brasil a baixo custo.",
         {})]]) + 0.1
    y = secao(slide, X1, y, LARGURA, "REFERÊNCIAS")
    texto(slide, X1, y, LARGURA, 1.2, [
        [("1. Brasil. Ministério da Saúde. CNES. Disponível em: cnes.datasus.gov.br. Acesso em: out. 2026.",
          {"tam": 8})],
        [("2. Brasil. Ministério da Saúde. SIH/SUS – TabNet. Disponível em: tabnet.datasus.gov.br. "
          "Acesso em: out. 2026.", {"tam": 8})],
        [("3. IBGE. Censo Demográfico 2022: pessoas com deficiência (SIDRA, tabela 10125). Acesso em: out. 2026.",
          {"tam": 8})],
    ])


def main() -> None:
    prs = Presentation(str(TEMPLATE))
    slide = prs.slides[0]
    cabecalho(slide)
    coluna_esquerda(slide)
    coluna_direita(slide)
    conclusoes(slide, 22.55)
    prs.save(str(SAIDA))
    print(f"salvo: {SAIDA.name}")


if __name__ == "__main__":
    main()
