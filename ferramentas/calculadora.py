#!/usr/bin/env python3
"""Calculadora de viabilidade: afiliado Mercado Livre + Meta Ads.

Responde a pergunta central antes de gastar qualquer real:
"com esta comissão, este preço e esta conversão, quanto posso pagar por clique
(ou por membro de grupo) e ainda recuperar o investimento?"

Modos:
  direto  anúncio que leva ao link de afiliado (direto ou via página ponte)
  tabela  sensibilidade: lucro por R$ 100 de verba para vários CPCs x conversões
  grupo   anúncio para captar membros de um grupo/canal de ofertas

Percentuais entram como número (12 = 12%). CPC, custo por membro e verba são os
valores exibidos no Gerenciador de Anúncios, sem impostos; o imposto sobre a
mídia paga no Brasil entra separado em --imposto-meta.

Exemplos:
  python3 ferramentas/calculadora.py direto --preco 189.90 --comissao 12 --cpc 0.35 --verba 300
  python3 ferramentas/calculadora.py tabela --preco 189.90 --comissao 12
  python3 ferramentas/calculadora.py grupo --custo-membro 1.20 --comissao-media 9 --verba 500
"""

import argparse

# Hipóteses padrão. Todas são pontos de partida a substituir por dados reais
# (painel de afiliado, Gerenciador de Anúncios) assim que a campanha rodar.
IMPOSTO_META_PCT = 13.83  # tributos somados à verba no Brasil (ver docs/03)
CONVERSAO_PCT = 1.5  # clique que chega ao ML -> pedido, tráfego frio de rede social
CHEGADA_PCT = 75.0  # clique no link -> página do ML carregada com atribuição
CANCELAMENTO_PCT = 7.0  # pedidos cancelados/devolvidos (comissão estornada)


def pct(valor):
    return valor / 100.0


def num(valor, casas=0):
    """Número no formato brasileiro: 1.234,56."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(valor):
    return ("-R$ " if valor < 0 else "R$ ") + num(abs(valor), 2)


def sinal(valor):
    return ("+" if valor >= 0 else "-") + num(abs(valor))


def comissao_por_venda(args):
    """Comissão líquida esperada por pedido atribuído."""
    bruta = args.preco * pct(args.comissao + args.extra)
    if args.teto is not None:
        bruta = min(bruta, args.teto)
    bruta *= 1 + pct(args.bonus_carrinho)
    return bruta, bruta * (1 - pct(args.cancelamento))


def lucro_por_verba(verba, cpc, conversao_pct, chegada_pct, comissao_liq, imposto_pct):
    cliques = verba / cpc
    vendas = cliques * pct(chegada_pct) * pct(conversao_pct)
    receita = vendas * comissao_liq
    custo = verba * (1 + pct(imposto_pct))
    return cliques, vendas, receita, custo, receita - custo


def modo_direto(args):
    bruta, liquida = comissao_por_venda(args)
    fator_imposto = 1 + pct(args.imposto_meta)
    ganho_clique_ml = liquida * pct(args.conversao)
    ganho_clique_anuncio = ganho_clique_ml * pct(args.chegada)
    cpc_max = ganho_clique_anuncio / fator_imposto
    cpa_max = liquida / fator_imposto
    roas_min = args.preco / liquida if liquida else float("inf")

    print("== Viabilidade: tráfego direto para a oferta ==")
    print(f"Comissão bruta por venda ........ {brl(bruta)}")
    print(f"Comissão líquida (após cancel.) . {brl(liquida)}")
    print(f"Ganho por clique que chega ao ML  {brl(ganho_clique_ml)}")
    print(f"Ganho por clique no anúncio ..... {brl(ganho_clique_anuncio)}")
    print(f"CPC máximo no Gerenciador ....... {brl(cpc_max)}  <- acima disso, prejuízo")
    print(f"Custo por venda máximo .......... {brl(cpa_max)}")
    print(f"ROAS mínimo (vendas/gasto c/imp.) {num(roas_min, 1)}x")

    if args.cpc:
        conversao_min = args.cpc * fator_imposto / (liquida * pct(args.chegada)) * 100
        folga = (cpc_max / args.cpc - 1) * 100
        print()
        print(f"Com CPC de {brl(args.cpc)}:")
        print(f"  conversão mínima necessária ... {num(conversao_min, 2)}%")
        if folga < 0:
            print(f"  o CPC precisa cair ............ {abs(folga):.0f}% para empatar")
        else:
            print(f"  folga até o prejuízo .......... {folga:.0f}% de aumento no CPC")
        if args.verba:
            cliques, vendas, receita, custo, lucro = lucro_por_verba(
                args.verba, args.cpc, args.conversao, args.chegada, liquida, args.imposto_meta
            )
            print()
            print(f"Projeção para verba de {brl(args.verba)} (+ impostos):")
            print(f"  cliques ....................... {num(cliques)}")
            print(f"  vendas estimadas .............. {num(vendas, 1)}")
            print(f"  comissão estimada ............. {brl(receita)}")
            print(f"  custo total com impostos ...... {brl(custo)}")
            print(f"  resultado ..................... {brl(lucro)} (ROI {lucro / custo * 100:+.0f}%)")


def modo_tabela(args):
    _, liquida = comissao_por_venda(args)
    cpcs = [0.10, 0.15, 0.20, 0.30, 0.40, 0.60, 0.80, 1.00]
    conversoes = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    print(f"Resultado em R$ por R$ 100 de verba (comissão líquida {brl(liquida)}/venda,")
    print(f"chegada {num(args.chegada)}%, imposto {num(args.imposto_meta, 2)}%). Linhas: CPC; colunas: conversão.")
    print()
    print("CPC     " + "".join(f"{num(c, 1) + '%':>8}" for c in conversoes))
    for cpc in cpcs:
        linha = []
        for conv in conversoes:
            *_, lucro = lucro_por_verba(100, cpc, conv, args.chegada, liquida, args.imposto_meta)
            linha.append(f"{sinal(lucro):>8}")
        print(f"{brl(cpc)} " + "".join(linha))


def modo_grupo(args):
    fator_imposto = 1 + pct(args.imposto_meta)
    custo_membro = args.custo_membro * fator_imposto
    ganho_clique = args.comissao_media * pct(args.conversao_quente)

    print("== Viabilidade: captação de membros para grupo/canal de ofertas ==")
    print(f"Custo por membro com impostos ... {brl(custo_membro)}")
    print(f"Ganho por clique (público quente) {brl(ganho_clique)}")
    print()
    print("Mês  Receita/membro  Acumulado  Situação")
    acumulado = 0.0
    payback = None
    ativos = 1.0
    for mes in range(1, args.meses + 1):
        receita_mes = ativos * args.cliques_mes * ganho_clique
        acumulado += receita_mes
        if payback is None and acumulado >= custo_membro:
            payback = mes
        situacao = "pago" if acumulado >= custo_membro else "a recuperar"
        print(f"{mes:>3}  {brl(receita_mes):>14}  {brl(acumulado):>9}  {situacao}")
        ativos *= 1 - pct(args.churn)

    print()
    if payback:
        print(f"Retorno do custo do membro no mês {payback}.")
    else:
        print(f"Não recupera o custo do membro em {args.meses} meses com estas hipóteses.")
    ltv_roi = (acumulado / custo_membro - 1) * 100
    print(f"Valor por membro em {args.meses} meses: {brl(acumulado)} (ROI {ltv_roi:+.0f}%)")

    if args.verba:
        membros = args.verba / args.custo_membro
        print()
        print(f"Verba de {brl(args.verba)} (+ impostos) compra ~{num(membros)} membros")
        print(f"  receita esperada em {args.meses} meses: {brl(membros * acumulado)}")
        print(f"  custo total com impostos: {brl(args.verba * fator_imposto)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="modo", required=True)

    def comuns_oferta(p):
        p.add_argument("--preco", type=float, required=True, help="preço do produto (R$)")
        p.add_argument("--comissao", type=float, required=True, help="comissão da categoria (%%)")
        p.add_argument("--extra", type=float, default=0.0, help="comissão extra / ganhos extras (%%)")
        p.add_argument("--teto", type=float, help="teto de comissão por item, se houver (R$)")
        p.add_argument("--bonus-carrinho", type=float, default=0.0,
                       help="acréscimo esperado por outros itens comprados na mesma visita (%% da comissão)")
        p.add_argument("--cancelamento", type=float, default=CANCELAMENTO_PCT, help="pedidos cancelados (%%)")
        p.add_argument("--chegada", type=float, default=CHEGADA_PCT, help="cliques que chegam ao ML (%%)")
        p.add_argument("--imposto-meta", type=float, default=IMPOSTO_META_PCT, help="impostos sobre a verba (%%)")

    direto = sub.add_parser("direto", help="tráfego direto para a oferta")
    comuns_oferta(direto)
    direto.add_argument("--conversao", type=float, default=CONVERSAO_PCT, help="clique -> pedido (%%)")
    direto.add_argument("--cpc", type=float, help="CPC observado ou esperado no Gerenciador (R$)")
    direto.add_argument("--verba", type=float, help="verba do teste, sem impostos (R$)")
    direto.set_defaults(func=modo_direto)

    tabela = sub.add_parser("tabela", help="sensibilidade CPC x conversão")
    comuns_oferta(tabela)
    tabela.set_defaults(func=modo_tabela)

    grupo = sub.add_parser("grupo", help="captação de membros para grupo/canal")
    grupo.add_argument("--custo-membro", type=float, required=True, help="custo por membro no Gerenciador (R$)")
    grupo.add_argument("--comissao-media", type=float, required=True,
                       help="comissão líquida média por venda das ofertas postadas (R$)")
    grupo.add_argument("--conversao-quente", type=float, default=3.0, help="clique -> pedido no grupo (%%)")
    grupo.add_argument("--cliques-mes", type=float, default=2.0, help="cliques em ofertas por membro/mês")
    grupo.add_argument("--churn", type=float, default=15.0, help="membros que saem por mês (%%)")
    grupo.add_argument("--meses", type=int, default=6, help="horizonte de análise (meses)")
    grupo.add_argument("--verba", type=float, help="verba de captação, sem impostos (R$)")
    grupo.add_argument("--imposto-meta", type=float, default=IMPOSTO_META_PCT, help="impostos sobre a verba (%%)")
    grupo.set_defaults(func=modo_grupo)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
