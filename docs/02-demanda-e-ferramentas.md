# Demanda, oferta e ferramentas

Levantamento e testes de 2026-09-29, feitos a partir de um container em nuvem
(IP de datacenter, sem login do usuário). De um IP residencial logado, parte do que
está bloqueado aqui provavelmente abre.

## O que já roda automaticamente
`ferramentas/radar_ml.py` lê, sem login:
- **Ofertas por categoria-raiz** (`/ofertas?category=MLB…&page=N`, 48 itens por página):
  preço, preço anterior, desconto, nota, faixa de vendidos ("+10 mil"), Full, selos
  (MAIS VENDIDO, OFERTA DO DIA, RELÂMPAGO), link. A categoria vem do filtro, então a
  comissão sai direto da tabela oficial.
- **Mais Vendidos** (página raiz): 10 seções × ~20 itens, com posição, preço, Full e selo.
  A seção nem sempre é a categoria real do item (ex.: SSD em "Games") — confirmar.
- **Tendências** (`--tendencias`): 40 termos mapeados para categoria e comissão.
  ⚠ Em 2026-09-29 a lista de crescimento veio vazia e os termos pareciam de reserva
  ("presente dia das mães" em setembro). Usar só como pista.

Primeira execução: 1.034 itens lidos em 33 s, 59 descartados por conformidade
(suplementos, whey, cápsulas, gift cards), 13 por ticket acima de R$ 1.500.

## API do Mercado Livre
- **Sem token** só respondem `/categories/{id}` e `/sites/MLB/domain_discovery/search`
  (termo → categoria). O resto devolve 401/403.
- **Com token OAuth** (app grátis no DevCenter, permissão "Métricas do negócio", login
  único do usuário; token dura 6 h, refresh token de uso único):
  `/trends/MLB/{categoria}` (50 termos por semana: crescimento, desejados, populares),
  `/highlights/MLB/category/{id}` (top 20 por categoria), `/reviews/item/{id}`,
  `/items` (preço, Full).
- **Busca por palavra-chave** (`/sites/MLB/search`) responde 403 mesmo com token desde o
  início de 2026. Não conte com ela.

## Fora do Mercado Livre

| Fonte | Sinal | Acesso daqui |
|---|---|---|
| Google Trends | interesse relativo e buscas em ascensão no Google | RSS diário ok; `pytrends` funcionou, mas está arquivado e é frágil |
| Google Keyword Planner | volume de busca no Google | precisa de conta Ads; sem gasto mostra faixas |
| Biblioteca de Anúncios da Meta | quem anuncia o item, desde quando, quantas versões | só pela web (a API não cobre anúncios comerciais do Brasil); o conector oficial da Meta anuncia acesso à Biblioteca |
| Zoom / Buscapé | menor preço entre lojas, histórico de preço | parseável daqui |
| Promobit | likes, comentários por oferta | parseável daqui |
| Pelando | "temperatura" das ofertas | bloqueado (Cloudflare); abrir no navegador |
| TikTok Creative Center | produtos em alta, CTR/CVR de anúncios | app em JavaScript; abrir no navegador |

Como ler a Biblioteca de Anúncios: País = Brasil, "Todos os anúncios", só ativos, buscar
pelo nome do produto ou por "achadinhos". Sinais de anúncio que se paga: veiculação
iniciada há 30 dias ou mais, 3 ou mais versões do mesmo criativo, várias plataformas.

## Ferramentas pagas (não assinar por enquanto)

| Ferramenta | O que dá | Preço visto |
|---|---|---|
| Nubimetrics | demanda por categoria, preço médio, saturação | sob consulta, teste grátis |
| Real Trends | vendas aproximadas de concorrentes | R$ 115–445/mês |
| Avantpro (extensão) | vendas, concorrência, histórico de preço | R$ 59,90/mês |
| Metrify (extensão) | vendas, faturamento, conversão por visita | R$ 59,90–89,90/mês |
| Hunter Spy / Melicidade | score de produto, histórico de preço | teste grátis |

Começamos com as fontes grátis, o painel de afiliado e os dados da própria campanha.
Uma extensão de ~R$ 60/mês só entra se faltar estimativa de vendas por anúncio.

## Modelo de pontuação
Filtros eliminatórios: comissão 0%, item proibido/restrito (Meta ou ML), vendedor abaixo
de reputação amarela, ticket acima de ~R$ 1.500.

`Score = CPS × D × Q × K`
- **CPS** (comissão por venda) = preço × (comissão da categoria + Ganhos Extras) ×
  (1 − cancelamento).
- **D** (demanda) = nível (faixa de vendidos, posição no Mais Vendidos, Tendências) e
  tendência (Google Trends das últimas 4 semanas vs. 12 anteriores).
- **Q** (conversão provável) = nota, nº de avaliações, preço vs. menor preço do mercado,
  Full, selo, ticket (a compra precisa sair em 24 h).
- **K** (competição no Meta) = 0,7 sem ninguém anunciando (não validado), 1,0 com 1–5
  anunciantes e ao menos um há 30+ dias, 0,8 com 6–15, 0,5 acima de 15.

O radar calcula a triagem (CPS, D e Q com os sinais públicos) e ajusta a conversão pelo
ticket. K, Ganhos Extras, histórico de preço e Google Trends entram na análise dos
finalistas. Os pesos são hipóteses; recalibramos com as métricas reais do painel.

## Fontes
- https://developers.mercadolivre.com.br/pt_br/tendencias
- https://developers.mercadolivre.com.br/pt_br/mais-vendidos-no-mercado-livre
- https://developers.mercadolivre.com.br/pt_br/autenticacao-e-autorizacao
- https://developers.mercadolivre.com.br/pt_br/permissoes-funcionais
- https://developers.mercadolivre.com.br/pt_br/itens-e-buscas
- https://www.reclameaqui.com.br/mercado-livre/erro-403-forbidden-ao-acessar-endpoint-sitesmlbsearch-da-api-do-mercado-livre_4HqcUyVoCdJmt4Lv/
- https://transparency.meta.com/researchtools/ad-library-tools
- https://developers.google.com/search/apis/trends
- https://github.com/GeneralMills/pytrends/issues/636
- https://ads.tiktok.com/help/article/top-products
- https://www.real-trends.com/br/precos · https://avantpro.com.br/ · https://metrify.com.br/
- https://centrodepartners.mercadolivre.com.br/apps/nubimetrics
