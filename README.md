# Agente de campanhas — Afiliado Mercado Livre

Escolhe produtos do Mercado Livre com comissão alta e demanda alta, prova a viabilidade
financeira antes de gastar e opera as campanhas no Meta Ads, com cada real aprovado
pelo usuário.

## Comece por aqui
- Estratégia e plano até a Black Friday: [docs/04-estrategia.md](docs/04-estrategia.md)
- Método passo a passo (skill do agente): [.claude/skills/campanha-afiliado-ml/SKILL.md](.claude/skills/campanha-afiliado-ml/SKILL.md)
- Regras, comissões e pagamentos do programa: [docs/01-programa-afiliados-ml.md](docs/01-programa-afiliados-ml.md)
- Fontes de demanda e ferramentas: [docs/02-demanda-e-ferramentas.md](docs/02-demanda-e-ferramentas.md)
- Meta Ads (políticas, custos, estrutura de teste): [docs/03-meta-ads.md](docs/03-meta-ads.md)

## Ferramentas
Python 3.8+, só biblioteca padrão.
```
python3 ferramentas/radar_ml.py                  # ofertas do ML ordenadas por oportunidade
python3 ferramentas/radar_ml.py --tendencias     # termos em alta com categoria e comissão
python3 ferramentas/calculadora.py direto --preco 399 --comissao 16 --cpc 0.35 --verba 280
python3 ferramentas/calculadora.py tabela --preco 399 --comissao 16
python3 ferramentas/calculadora.py grupo --custo-membro 1.20 --comissao-media 9
```

## Situação
Pesquisa concluída em 2026-09-29. Próximo passo: preparação das contas (fase 0) e radar
focado no Dia das Crianças.
