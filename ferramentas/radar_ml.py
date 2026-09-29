#!/usr/bin/env python3
"""Radar de ofertas do Mercado Livre para afiliados.

Lê as páginas públicas de Ofertas (por categoria) e de Mais Vendidos, aplica a
tabela oficial de comissões do Programa de Afiliados, descarta o que não serve
para anúncio pago e ordena o resto por um índice de oportunidade.

O índice é triagem, não decisão: os primeiros colocados ainda passam por
Google Trends, Biblioteca de Anúncios, histórico de preço e pela calculadora.

Uso:
  python3 ferramentas/radar_ml.py
  python3 ferramentas/radar_ml.py --categorias MLB1132 MLB1246 --paginas 3 --top 40
  python3 ferramentas/radar_ml.py --saida radar/2026-09-29.md --csv radar/2026-09-29.csv
  python3 ferramentas/radar_ml.py --tendencias
"""

import argparse
import csv
import json
import math
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime

from calculadora import (CANCELAMENTO_PCT, CHEGADA_PCT, CONVERSAO_PCT, IMPOSTO_META_PCT, brl,
                         fator_ticket, num)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
API = "https://api.mercadolibre.com"

# Comissão por categoria-raiz, venda direta (mercadolivre.com.br/ajuda/27913, lida em 2026-09-29).
COMISSAO = {
    "MLB1246": ("Beleza e Cuidado Pessoal", 16),
    "MLB1430": ("Calçados, Roupas e Bolsas", 16),
    "MLB1276": ("Esportes e Fitness", 16),
    "MLB5672": ("Acessórios para Veículos", 12),
    "MLB1384": ("Bebês", 12),
    "MLB1132": ("Brinquedos e Hobbies", 12),
    "MLB1574": ("Casa, Móveis e Decoração", 12),
    "MLB263532": ("Ferramentas", 12),
    "MLB1144": ("Games", 12),
    "MLB3937": ("Joias e Relógios", 12),
    "MLB1196": ("Livros, Revistas e Comics", 12),
    "MLB1953": ("Mais Categorias", 12),
    "MLB1039": ("Câmeras e Acessórios", 5),
    "MLB1051": ("Celulares e Telefones", 5),
    "MLB5726": ("Eletrodomésticos", 5),
    "MLB1000": ("Eletrônicos, Áudio e Vídeo", 5),
    "MLB1648": ("Informática", 5),
}
# Fora da tabela explícita: assumimos 12%, mas é preciso confirmar no painel de afiliado.
A_CONFIRMAR = {
    "MLB1368": "Arte, Papelaria e Armarinho",
    "MLB12404": "Festas e Lembrancinhas",
    "MLB1182": "Instrumentos Musicais",
    "MLB1367": "Antiguidades e Coleções",
    "MLB1168": "Música, Filmes e Seriados",
    "MLB1499": "Indústria e Comércio",
    "MLB271599": "Agro",
    "MLB1500": "Construção",  # 12% na tabela, mas fora da lista de elegíveis (ajuda/30088)
}
# Sem comissão ou fora da lista de categorias elegíveis.
EXCLUIDAS = {"MLB1403": "Alimentos e Bebidas", "MLB264586": "Saúde", "MLB1071": "Pet Shop"}

PADRAO = [cat for cat, (_, taxa) in COMISSAO.items() if taxa >= 12]

# Itens que o programa ou as políticas da Meta barram ou restringem em anúncio pago.
# Cosmético "com colágeno/vitamina" passa; cápsula, pó proteico e afins não.
BLOQUEIO = re.compile(
    r"vape|pod descart|cigarro eletr|narguil|tabaco|peptide|creatina|whey|proteina|suplement|"
    r"capsulas?\b|comprimidos?\b|melatonina|polivitaminico|multivitaminico|termogen|emagrec|"
    r"remedio|medicament|anabol|esteroide|injetavel|masteron|oxandrolona|testosterona|ozempic|"
    r"mounjaro|semaglutida|tirzepatida|sibutramina|minoxidil|canabid|\bcbd\b|"
    r"arma de fogo|revolver|municao|airsoft|espingarda|"
    r"gift ?card|cartao presente|recarga|razer gold|playstation store|ingresso|erotic|sex ?shop|"
    r"vibrador|lubrificante intimo|\b(cerveja|vinho|whisky|vodka|cachaca|gin|licor)\b|lente de contato"
)


class Bloqueado(Exception):
    """A página pediu login ou não trouxe os dados esperados."""


def sem_acento(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def baixar(url, tentativas=3):
    """Baixa a página e devolve o JSON de estado embutido (_n.ctx.r)."""
    for tentativa in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                final, html = resp.geturl(), resp.read().decode("utf-8", errors="replace")
            break
        except OSError:
            if tentativa == tentativas - 1:
                raise
            time.sleep(2 ** (tentativa + 1))
    marcador = "_n.ctx.r="
    if "account-verification" in final or marcador not in html:
        raise Bloqueado(url)
    dados, _ = json.JSONDecoder().raw_decode(html[html.index(marcador) + len(marcador):])
    return dados


def api(caminho):
    req = urllib.request.Request(API + caminho, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def cartoes(no, secao=None, cat_secao=None):
    """Percorre o JSON da página e devolve (cartão, seção, categoria da seção)."""
    if isinstance(no, dict):
        meta = no.get("metadata")
        if isinstance(meta, dict) and str(meta.get("id", "")).startswith("MLB") and isinstance(no.get("components"), list):
            yield no, secao, cat_secao
            return
        if isinstance(no.get("title"), str):
            secao = no["title"]
        cat_secao = (no.get("best_sellers_configuration") or {}).get("category", cat_secao)
        for valor in no.values():
            yield from cartoes(valor, secao, cat_secao)
    elif isinstance(no, list):
        for valor in no:
            yield from cartoes(valor, secao, cat_secao)


def ler_vendidos(texto):
    achado = re.search(r"(\d+(?:[.,]\d+)?)\s*(mil)?\s*vendid", texto)
    if not achado:
        return None
    valor = float(achado.group(1).replace(",", "."))
    return int(valor * 1000) if achado.group(2) else int(valor)


def ler_cartao(cartao):
    comps = {c.get("type"): c for c in cartao.get("components", [])}
    meta = cartao["metadata"]
    preco_info = (comps.get("price") or {}).get("price") or {}
    anterior = None
    for rotulo in preco_info.get("price_labels", []):
        for valor in rotulo.get("values", []):
            if valor.get("key") == "previous_price":
                anterior = (valor.get("price") or {}).get("value")
    nota = vendidos = None
    for valor in ((comps.get("review_compacted") or {}).get("review_compacted") or {}).get("values", []):
        texto = (valor.get("label") or {}).get("text", "")
        if valor.get("key") == "label" and re.fullmatch(r"\d(?:[.,]\d)?", texto):
            nota = float(texto.replace(",", "."))
        elif "vendid" in texto:
            vendidos = ler_vendidos(texto)
    selos = []
    for widget in cartao.get("widget_components", []):
        for rotulo in (widget.get("poly_label_component") or {}).get("labels", []):
            texto = rotulo.get("text", "")
            limpo = "RELÂMPAGO" if "icon_thunder" in texto else re.sub(r"\{[^}]*\}\s*", "", texto).strip()
            if limpo:
                selos.append(limpo)
    preco = (preco_info.get("current_price") or {}).get("value")
    desconto = round((1 - preco / anterior) * 100) if preco and anterior else 0
    url = meta.get("url", "")
    return {
        "id": meta["id"],
        "titulo": ((comps.get("title") or {}).get("title") or {}).get("text", "").strip(),
        "preco": preco,
        "preco_anterior": anterior,
        "desconto": desconto,
        "nota": nota,
        "vendidos": vendidos,
        "full": bool(re.search(r"icon_full|full_icon", json.dumps(comps.get("shipping_v2", {})))),
        "selos": selos,
        "url": url if url.startswith("http") else "https://" + url,
    }


def taxa_da_categoria(cat):
    if cat in COMISSAO:
        nome, taxa = COMISSAO[cat]
        return nome, taxa, ""
    if cat in A_CONFIRMAR:
        return A_CONFIRMAR[cat], 12, "confirmar comissão"
    if cat in EXCLUIDAS:
        return EXCLUIDAS[cat], 0, "categoria excluída"
    return cat or "?", 12, "confirmar comissão"


def coletar(args):
    itens, avisos = {}, []

    def guardar(item, cat, origem, posicao=None):
        nome, taxa, alerta = taxa_da_categoria(cat)
        item.update(categoria=nome, comissao_pct=taxa, alerta=alerta, origem=origem, posicao=posicao)
        atual = itens.get(item["id"])
        if atual is None:
            itens[item["id"]] = item
            return
        # Mesmo item em duas páginas: junta os sinais.
        for chave in ("nota", "vendidos", "preco_anterior", "posicao"):
            atual[chave] = atual.get(chave) or item.get(chave)
        atual["desconto"] = max(atual["desconto"], item["desconto"])
        atual["selos"] = sorted(set(atual["selos"]) | set(item["selos"]))
        atual["origem"] = " + ".join(sorted({*atual["origem"].split(" + "), origem}))

    for cat in args.categorias:
        for pagina in range(1, args.paginas + 1):
            url = f"https://www.mercadolivre.com.br/ofertas?category={cat}&page={pagina}"
            try:
                dados = baixar(url)
            except (Bloqueado, OSError) as erro:
                avisos.append(f"Ofertas {cat} p.{pagina}: {type(erro).__name__}")
                break
            lidos = [ler_cartao(c) for c, _, _ in cartoes(dados)]
            for item in lidos:
                guardar(item, cat, "Ofertas")
            if len(lidos) < 48:
                break
            time.sleep(args.pausa)

    if not args.sem_mais_vendidos:
        try:
            dados = baixar("https://www.mercadolivre.com.br/mais-vendidos")
            contagem = {}
            for cartao, secao, cat_secao in cartoes(dados):
                contagem[secao] = contagem.get(secao, 0) + 1
                item = ler_cartao(cartao)
                item["alerta_secao"] = True
                guardar(item, cat_secao, "Mais vendidos", contagem[secao])
        except (Bloqueado, OSError) as erro:
            avisos.append(f"Mais vendidos: {type(erro).__name__}")
    return list(itens.values()), avisos


def clip(valor):
    return min(1.0, max(0.0, valor))


def avaliar(item, args):
    liquida = item["preco"] * item["comissao_pct"] / 100 * (1 - args.cancelamento / 100)
    conversao = args.conversao * fator_ticket(item["preco"])
    epc = liquida * conversao / 100 * args.chegada / 100
    item["comissao_liq"] = liquida
    item["cpc_max"] = epc / (1 + args.imposto_meta / 100)

    # Demanda: faixa de vendidos (escala log, 10 mil = 1) ou posição no Mais Vendidos.
    d_vendidos = clip(math.log10(1 + item["vendidos"]) / 4) if item["vendidos"] else 0
    d_posicao = (21 - item["posicao"]) / 20 if item.get("posicao") else 0
    demanda = max(d_vendidos, d_posicao)

    # Sinais de que o anúncio converte: nota, selo, Full e desconto.
    selo = 1 if "MAIS VENDIDO" in item["selos"] else 0.5 if item["selos"] else 0
    confianca = 0.2 + 0.8 * (
        0.35 * clip((item["nota"] or 4.0) - 4.0)
        + 0.25 * selo
        + 0.20 * (1 if item["full"] else 0)
        + 0.20 * clip(item["desconto"] / 50)
    )
    item["indice"] = item["cpc_max"] * 100 * (0.2 + 0.8 * demanda) * confianca


def filtrar(itens, args):
    aprovados, descartes = [], {"conformidade": [], "comissão zero": [], "ticket alto": [], "sem preço": []}
    for item in itens:
        if not item["preco"]:
            descartes["sem preço"].append(item)
        elif item["comissao_pct"] == 0:
            descartes["comissão zero"].append(item)
        elif BLOQUEIO.search(sem_acento(item["titulo"])):
            descartes["conformidade"].append(item)
        elif item["preco"] > args.ticket_max:
            descartes["ticket alto"].append(item)
        else:
            avaliar(item, args)
            aprovados.append(item)
    aprovados.sort(key=lambda i: i["indice"], reverse=True)
    return aprovados, descartes


def celula(texto):
    return texto.replace("|", "/").replace("[", "(").replace("]", ")")


def relatorio(aprovados, descartes, avisos, total, args):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    linhas = [
        f"# Radar de ofertas — {agora}",
        "",
        f"Fontes: Ofertas do Mercado Livre ({len(args.categorias)} categorias × até {args.paginas} páginas)"
        + ("" if args.sem_mais_vendidos else " e Mais Vendidos") + f". {total} itens lidos, {len(aprovados)} aprovados.",
        "Descartados: " + ", ".join(f"{len(v)} por {k}" for k, v in descartes.items() if v) + ".",
        f"Hipóteses do CPC máximo: conversão {num(args.conversao, 1)}% até R$ 150, reduzida em preços maiores "
        f"(×0,75 até R$ 400, ×0,5 até R$ 800, ×0,35 acima); chegada {num(args.chegada)}%, "
        f"cancelamento {num(args.cancelamento)}%, imposto Meta {num(args.imposto_meta, 2)}%.",
        "O índice é triagem: confirme categoria e Ganhos Extras no painel de afiliado e valide a demanda antes de anunciar.",
    ]
    if avisos:
        linhas.append("Avisos de coleta: " + "; ".join(avisos) + ".")
    linhas += [
        "",
        "| # | Produto | Categoria (comissão) | Preço | Desc. | Nota | Vendidos | Selos | Comissão líq. | CPC máx | Índice | Alerta |",
        "|---|---------|----------------------|-------|-------|------|----------|-------|---------------|---------|--------|--------|",
    ]
    for pos, item in enumerate(aprovados[: args.top], 1):
        alertas = [item["alerta"]] if item["alerta"] else []
        if item.get("alerta_secao") and "Ofertas" not in item["origem"]:
            alertas.append("categoria da seção")
        vendidos = f"+{num(item['vendidos'])}" if item["vendidos"] else (f"top {item['posicao']}" if item.get("posicao") else "")
        linhas.append(
            f"| {pos} | [{celula(item['titulo'][:60].strip())}]({item['url'].split('#')[0]}) | {item['categoria']} ({item['comissao_pct']}%) "
            f"| {brl(item['preco'])} | {item['desconto']}% | {num(item['nota'], 1) if item['nota'] else ''} | {vendidos} "
            f"| {celula(', '.join(item['selos']))}{' Full' if item['full'] else ''} | {brl(item['comissao_liq'])} "
            f"| {brl(item['cpc_max'])} | {num(item['indice'], 2)} | {', '.join(alertas)} |"
        )
    if args.mostrar_descartes and descartes["conformidade"]:
        linhas += ["", "Descartados por conformidade:"]
        linhas += [f"- {item['titulo'][:80]} ({brl(item['preco'] or 0)})" for item in descartes["conformidade"]]
    return "\n".join(linhas) + "\n"


def gravar_csv(caminho, aprovados):
    campos = ["id", "titulo", "categoria", "comissao_pct", "preco", "preco_anterior", "desconto", "nota",
              "vendidos", "posicao", "full", "selos", "comissao_liq", "cpc_max", "indice", "alerta", "origem", "url"]
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        for item in aprovados:
            escritor.writerow({**item, "selos": "; ".join(item["selos"])})


def tendencias(args):
    """Termos em alta no ML, com a categoria e a comissão prováveis de cada um."""
    pagina = baixar("https://tendencias.mercadolivre.com.br/")["appProps"]["pageProps"]
    listas = [("increasedSearchGrowthTrends", "maior crescimento"),
              ("higherRevenueTrends", "mais desejadas"),
              ("shortTailTrends", "mais populares")]
    if not (pagina.get("increasedSearchGrowthTrends") or {}).get("trends"):
        print("Aviso: a lista de maior crescimento veio vazia; a página pode estar exibindo termos de reserva.\n")
    print("| Lista | Termo | Categoria provável | Comissão | Alerta |")
    print("|-------|-------|--------------------|----------|--------|")
    raizes = {}
    for chave, rotulo in listas:
        for termo in (pagina.get(chave) or {}).get("trends", []):
            palavra = termo.get("keyword", "")
            categoria = termo.get("previous_category_id")
            try:
                achado = api("/sites/MLB/domain_discovery/search?limit=1&q=" + urllib.parse.quote(palavra))
                categoria = achado[0]["category_id"] if achado else categoria
                if categoria and categoria not in raizes:
                    raizes[categoria] = api(f"/categories/{categoria}")["path_from_root"][0]["id"]
                    time.sleep(0.2)
            except (OSError, KeyError, IndexError, ValueError):
                pass
            nome, taxa, alerta = taxa_da_categoria(raizes.get(categoria))
            if BLOQUEIO.search(sem_acento(palavra)):
                alerta = "conformidade"
            print(f"| {rotulo} | {palavra} | {nome} | {taxa}% | {alerta} |")
            time.sleep(0.2)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--categorias", nargs="+", default=PADRAO,
                        help="IDs de categoria-raiz (padrão: todas com comissão de 12%% ou 16%%)")
    parser.add_argument("--paginas", type=int, default=2, help="páginas de Ofertas por categoria (48 itens cada)")
    parser.add_argument("--top", type=int, default=30, help="linhas no relatório")
    parser.add_argument("--ticket-max", type=float, default=1500, help="descarta preços acima deste valor (R$)")
    parser.add_argument("--conversao", type=float, default=CONVERSAO_PCT, help="clique -> pedido (%%)")
    parser.add_argument("--chegada", type=float, default=CHEGADA_PCT, help="cliques que chegam ao ML (%%)")
    parser.add_argument("--cancelamento", type=float, default=CANCELAMENTO_PCT, help="pedidos cancelados (%%)")
    parser.add_argument("--imposto-meta", type=float, default=IMPOSTO_META_PCT, help="impostos sobre a verba (%%)")
    parser.add_argument("--pausa", type=float, default=1.0, help="segundos entre páginas")
    parser.add_argument("--sem-mais-vendidos", action="store_true", help="não lê a página Mais Vendidos")
    parser.add_argument("--mostrar-descartes", action="store_true", help="lista os descartados por conformidade")
    parser.add_argument("--saida", help="grava o relatório Markdown neste arquivo")
    parser.add_argument("--csv", help="grava todos os aprovados neste CSV")
    parser.add_argument("--tendencias", action="store_true", help="lista os termos em alta e sai")
    args = parser.parse_args()

    if args.tendencias:
        tendencias(args)
        return

    itens, avisos = coletar(args)
    if not itens:
        sys.exit("Nenhum item coletado: " + ("; ".join(avisos) or "páginas vazias"))
    aprovados, descartes = filtrar(itens, args)
    texto = relatorio(aprovados, descartes, avisos, len(itens), args)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)
    if args.csv:
        gravar_csv(args.csv, aprovados)
    print(texto)


if __name__ == "__main__":
    main()
