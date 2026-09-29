---
name: campanha-afiliado-ml
description: Método do agente de campanhas de afiliado do Mercado Livre. Use ao escolher produtos para divulgar (cruzar comissão com demanda), calcular viabilidade (CPC e custo por venda máximos, retorno de grupo/canal), montar ou revisar campanhas no Meta Ads, definir verba e regras de corte e escala, ou analisar resultados de campanhas de afiliado.
---

# Campanha de afiliado Mercado Livre

Cada ciclo põe verba só onde a conta fecha e mede rápido o bastante para cortar o que
não fecha. Regras do projeto em `CLAUDE.md`; fatos e fontes em `docs/01`–`04`.

## Regras que valem sempre
1. Nada é ativado sem "aprovado" explícito do usuário para valor, período e anúncios.
   Tudo nasce pausado, com limite de gastos da conta configurado.
2. Toda recomendação de verba mostra a saída da calculadora e as hipóteses usadas.
3. Conformidade antes de performance: Termos do ML (docs/01) e políticas da Meta (docs/03).
4. Preço e desconto anunciados precisam estar vigentes; pausar quando a oferta muda.
5. Cada campanha tem arquivo em `campanhas/`, criado a partir de `_modelo-plano.md`.

## 1. Radar: comissão × demanda
```
python3 ferramentas/radar_ml.py --saida radar/AAAA-MM-DD.md --csv radar/AAAA-MM-DD.csv
python3 ferramentas/radar_ml.py --categorias MLB1132 MLB1384 --paginas 4   # foco sazonal
python3 ferramentas/radar_ml.py --tendencias                              # termos em alta
```
Categorias sazonais: Brinquedos (MLB1132), Bebês (MLB1384) e Games (MLB1144) antes de
12/10; Beleza (MLB1246), Moda (MLB1430), Esportes (MLB1276) e Casa (MLB1574) na Black
Friday.

## 2. Finalistas (5–10 do topo do radar)
- Categoria e comissão reais + Ganhos Extras: barra de afiliados/Central (navegador do usuário).
- Demanda externa: Google Trends Brasil, 90 dias (subindo, estável ou caindo); Promobit.
- Preço: menor preço no Zoom/Buscapé; se o ML não é o mais barato, a conversão cai.
- Concorrência (K): Biblioteca de Anúncios — quantos anunciam o item e há quanto tempo.
- Vendedor: reputação amarela ou melhor, Full, nota ≥ 4,5 com 100+ avaliações.
- Ordenar por `Score = CPS × D × Q × K` (docs/02) e escolher 1–3 produtos ou uma lista.

## 3. Viabilidade
```
python3 ferramentas/calculadora.py direto --preco P --comissao C [--extra E] --cpc 0.40 --verba V
python3 ferramentas/calculadora.py tabela --preco P --comissao C
python3 ferramentas/calculadora.py grupo --custo-membro 1.20 --comissao-media 9
```
Seguir só se o CPC esperado (benchmark ou histórico da conta) ficar abaixo do CPC máximo
com CTR alcançável: CTR necessário = CPM ÷ (10 × CPC máximo). Acima de ~3%, só com
criativo já validado ou data comemorativa.

## 4. Montagem
1. Gerar um link por criativo no gerador oficial, cada um com sua etiqueta
   (`<campanha>-<conjunto>-<criativo>`, ≤ 30 caracteres).
2. Estrutura padrão (docs/03): Tráfego → visualização da página de destino; ABO; 1–2
   conjuntos; 3–5 criativos; Brasil 18+; Advantage+ sem Audience Network.
3. Checklist: sem marca/logo do ML; #publi; preço real; conteúdo próprio; categoria
   permitida; público 18+; link do gerador oficial sem encurtador.
4. Criar tudo pausado — conector oficial da Meta, navegador do usuário ou passo a passo.
5. Preencher o plano em `campanhas/` e pedir aprovação com o custo total já com impostos.

## 5. Leitura e decisão (D+1, D+2, D+3, D+7)
- Meta: gasto, CPM, CTR de link, CPC, visualizações da página, frequência.
- ML (por etiqueta): cliques, vendas brutas, ganhos, status das vendas.
- Chegada = cliques no painel ML ÷ cliques de link na Meta.
- EPC real = ganhos ÷ cliques no painel ML. CPC máximo real = EPC × chegada ÷ 1,1383.
- Cortar: CTR < 1% após ~1.000 impressões; gasto ≥ 2,5× o custo por venda máximo sem
  venda; frequência > 2,5–3 com CTR caindo; qualquer venda "Recusada – Publicidade não
  permitida" pausa tudo e vai para o usuário.
- Escalar: ROI ≥ 0 com 3+ vendas → +20–30% a cada 48 h ou duplicar o vencedor.

## 6. Fechamento
Atualizar o arquivo da campanha com números e decisão; recalibrar as hipóteses da
calculadora (conversão, chegada, cancelamento) com os dados reais.
