# Meta Ads para afiliado Mercado Livre

Levantamento de 2026-09-29. Tipos de fonte: **[OF]** oficial (Meta, ML, governo),
**[DADO]** base de terceiros com metodologia, **[PR]** praticante, **[AN]** anedota.

## O que decide
- O ML permite anúncio no Facebook/Instagram **a partir das contas do afiliado
  cadastradas no programa** (cl. 4.4). A página/perfil que anuncia precisa estar declarada.
- Só conta compra feita em até **24 h** após o clique.
- **Custo real = gasto do Gerenciador × 1,1383** (PIS/Cofins 9,25% + ISS 2,9% por dentro,
  desde 2026-01-01) [OF].
- Não dá para pôr Pixel no ML: venda se mede pelas **etiquetas** do painel de afiliado;
  a Meta só vê cliques e visualizações de página.

## Políticas que importam
- **Link de afiliado direto**: nenhuma proibição nos Padrões de Publicidade; o produto do
  anúncio precisa ser o mesmo da página de destino [OF].
- **Proibido** (Spam, Integridade de Conta): cloaking, link que entrega outra coisa,
  redirecionamento que troca de domínio após uma ação, interface enganosa, imitar marca
  ou domínio, criar conta para fugir de restrição [OF].
- **Preço riscado/desconto só se for real** no momento (Práticas Comerciais Proibidas) [OF].
- **Marca Mercado Livre**: nada de logo, nome de página "Ofertas Mercado Livre" ou visual
  de canal oficial (ML cl. 2.3/4.4 e política de PI da Meta). Citar "no Mercado Livre" no
  texto: não confirmado — evitar até o suporte responder.
- **Categorias a evitar**: suplementos/emagrecimento (restritos, 18+), álcool, armas,
  medicamentos, cripto/financeiro [OF]. O radar já descarta esses itens.
- **Menores**: o ECA Digital (Lei 15.211/2025, em vigor desde 2026-03-17) proíbe anúncio
  por perfilamento para menores. Dia das Crianças: público 18+, texto para os pais [OF].
- **Identificação de publicidade**: #publi (ML cl. 5.1, guia do CONAR de mai/2026).
- **Conteúdo próprio**: criativo precisa ser seu ou licenciado; o ML proíbe copiar
  materiais do site e impulsionar conteúdo de outros creators.

## Conta de anúncios
- Conta nova tem limite diário definido pela Meta; muitas reprovações restringem a conta
  (recurso pelo Account Quality) [OF].
- A Meta quer 90% da receita vindo de anunciantes verificados até o fim de 2026, e o
  Decreto 12.975/2026 + Portaria MJSP de 2026-09-23 obrigam as plataformas a registrar o
  CPF/CNPJ de quem paga [OF]. Ter a verificação de identidade/empresa em dia.
- Pagamento: cartão é pós-pago (imposto na fatura); Pix, boleto e Mercado Pago são
  pré-pagos (R$ 100 rendem ~R$ 87,85 de mídia).
- Configurar **limite de gastos da conta** como trava de segurança antes de ativar.

## Rastreio e otimização
- **Etiqueta por anúncio** no gerador de links (até 30 caracteres, só minúsculas e
  números, criada pelo computador); painel atualiza a cada ~3 h; ganho confirmado só após
  a validação.
- **Tráfego direto ao ML**: otimizar por **visualização da página de destino** (funciona
  sem Pixel desde ago–set/2025, medição modelada) e **excluir a Audience Network**. Num
  teste público, otimizar por clique mandou 99% dos cliques para a Audience Network [PR].
- **Página própria** (presell/lista com Pixel + API de Conversões): evento no clique de
  saída para o ML → conversão personalizada → campanha de Vendas/Leads otimizando esse
  evento. Ganha remarketing e públicos próprios. Exige domínio declarado como mídia.
- **Públicos sem Pixel**: quem assistiu aos vídeos (ThruPlay/50%), quem interagiu com o
  perfil/página. Servem para remarketing na Black Friday.
- Aprendizado: ~50 eventos por conjunto em 7 dias; edição grande reinicia [OF].
- Atribuição: desde 2026-03 só clique no link conta como atribuição por clique [OF].

## Benchmarks Brasil

| Métrica | Valor | Tipo |
|---|---|---|
| CPM mediano (todas as indústrias) | ~US$ 3,46 (jul/25–jul/26); jul/26 US$ 6,76 | DADO |
| CPM por posicionamento | IG feed R$ 12–25 · Stories/Reels R$ 8–18 · FB feed R$ 6–15 | PR |
| CPC mediano (todos os cliques) | ~US$ 0,20; jul/26 US$ 0,26 | DADO |
| CPC e-commerce | R$ 0,30–1,50 | PR |
| CTR mediano | ~1,7%; jul/26 ~3,0% | DADO |
| Custo por membro de grupo de ofertas | R$ 0,60–1,80 (2–3 de cada 10 cliques entram) | AN |
| Custo por seguidor no Instagram | R$ 0,70–1,50 | AN |
| Clique → compra, tráfego social frio | Amazon ~2% (EUA, 2023); ML/Shopee sem dado público | DADO |

CPM e concorrência sobem perto do Dia das Crianças e da Black Friday.

**CTR de link necessário para empatar** = CPM ÷ (10 × CPC máximo).
Ex.: CPM R$ 15 e CPC máximo R$ 0,50 → CTR ≥ 3%. CPM R$ 10 → 2%.
O criativo é a principal alavanca de lucro.

## Estrutura de teste (R$ 30–100/dia)
- **Objetivo**: Tráfego → visualizações da página de destino (link do ML com etiqueta).
  Com página própria: Vendas/Leads no evento de clique de saída.
- **Estrutura**: 1 campanha, orçamento por conjunto (ABO) para comparar ângulos; 1–2
  conjuntos de R$ 15–50/dia; 3–5 criativos diferentes por conjunto.
- **Público**: amplo, Brasil, 18+ (25–54 no Dia das Crianças); variar criativo pesa mais
  que refinar interesse. **Posicionamentos**: Advantage+ sem Audience Network.
- **Duração**: ler interesse após ~1.000 impressões por anúncio; vendas após 48–72 h;
  teste A/B por 7 dias.

## Regras de corte e escala
- CTR de link < 1% após ~1.000 impressões → pausar o anúncio (piso de praticante: 0,5%).
- CTR abaixo do necessário para empatar → trocar gancho/criativo.
- Gasto de 2,5× o custo por venda máximo sem venda na etiqueta → pausar.
- Frequência > 2,5–3 em 7 dias com CTR caindo → novo criativo.
- Escala: +20–30% de orçamento a cada 48 h, ou duplicar o vencedor; saltos grandes
  reiniciam o aprendizado.

## Criativos que funcionam para oferta
- Vídeo vertical 9:16 com o produto em uso nos 2 primeiros segundos ("achadinho").
- Carrossel em que cada card leva ao produto exato, ou a uma lista de afiliado.
- Preço e desconto reais, com data; contagem regressiva para a data comemorativa;
  anúncios de lembrete na Black Friday.
- Sempre #publi, sem logo ou visual do ML.

## Como vou operar a conta
1. **Conector oficial da Meta** (Meta Ads AI Connectors, beta aberto desde 2026-04-29,
   sem custo no beta): claude.ai → Configurações → Conectores → Adicionar conector
   personalizado → `https://mcp.facebook.com/ads` → login no Facebook escolhendo só a
   conta/página certas. Depois, abrir uma nova sessão. Permite ler métricas, criar
   campanhas/conjuntos/anúncios (nascem pausados), ajustar orçamento e consultar a
   Biblioteca de Anúncios. Não sobe imagem/vídeo do computador: o criativo precisa estar
   numa URL ou já na conta.
2. **Navegador**: Claude Code no computador do usuário com a extensão Claude in Chrome
   (`claude --chrome`), usando a sessão já logada no Gerenciador e na Central de Afiliados.
3. **Manual**: eu entrego o passo a passo com todos os campos; o usuário clica.

Em qualquer caminho: tudo criado pausado, ativação só com "aprovado".

## Fontes
- Padrões de Publicidade: https://transparency.meta.com/policies/ad-standards/
- Spam: https://transparency.meta.com/policies/community-standards/spam/
- Práticas comerciais proibidas: https://transparency.meta.com/policies/ad-standards/deceptive-content/prohibited-commercial-practices/
- Saúde e bem-estar: https://transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/
- Impostos no Brasil: https://www.facebook.com/business/help/471651647527469 · https://tecnoblog.net/noticias/meta-decide-repassar-os-custos-com-impostos-no-brasil-para-os-anunciantes/
- Fase de aprendizado: https://www.facebook.com/business/help/112167992830700
- Edições significativas: https://www.facebook.com/business/help/316478108955072
- LPV sem Pixel: https://www.linkedin.com/posts/jonloomer_no-pixel-required-for-landing-page-views-activity-7369334672742412291-ZRwc
- Qualidade de tráfego por otimização: https://www.jonloomer.com/split-test-which-optimization-leads-to-the-most-high-quality-traffic/
- Benchmarks: https://www.superads.ai/facebook-ads-costs/cpm-cost-per-mille/brazil · https://www.intentmarketing.com.br/blog/post-quanto-custa-meta-ads
- ECA Digital: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15211.htm
- Transparência de anunciantes: https://olhardigital.com.br/2026/09/24/internet-e-redes-sociais/redes-sociais-terao-de-revelar-quem-paga-por-anuncios-sob-novas-regras-do-ministerio-da-justica
- Regras de corte: https://admanage.ai/blog/when-to-kill-a-facebook-ad
- Conector oficial: https://www.facebook.com/business/news/meta-ads-ai-connectors · https://ferrerponseti.com/en/blog/official-meta-ads-mcp-claude/
- Claude Code + Chrome: https://code.claude.com/docs/en/chrome
