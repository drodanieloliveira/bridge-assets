# Agente de Instagram — Bridge & Co. (@danielbridgeco)

Repositório público usado para hospedar as imagens dos carrosséis e a fila de publicação.
As imagens são servidas pelo link `raw_base` + caminho, que o Instagram consegue baixar.

## Arquivos
- `queue.json` — fila de posts. Cada post tem `date`, `dir`, `slides`, `caption`, `approved`, `published`, `media_id`
- `posts/<semana>/slides.json` — texto dos slides de cada semana
- `posts/<semana>/diaNN/1.jpg … 6.jpg` — slides renderizados (1080×1350, JPEG)
- `tools/render.py` — renderizador com visuais variados (search, split, calendar, checklist, notif, chat, icons, bignum, stars) e temas navy/cream/gold; uso: `python3 tools/render.py posts/<semana>/slides.json posts/<semana> tools/fonts`

## Regras de publicação
- só publicar post com `approved: true` e `published: false`
- nunca publicar post que não foi aprovado pelo Daniel no chat
- publicar um post por dia, o de `date` igual a hoje (fuso America/New_York)
- carrossel via Windsor.ai, conector `instagram`, ação `create_carousel_post`, conta `danielbridgeco`
- depois de publicar: gravar `published: true` e o `media_id` em `queue.json` e fazer commit

## Regras de conteúdo
- público: donos brasileiros de negócios nos EUA — dona de house cleaning e dono de construção/remodeling
- alternar os dois avatares; PT-BR; CTA com palavra-chave de direct
- sem promessa de faturamento ou número de clientes; sem depoimento inventado
- visual: navy #0B1F3A, dourado #C9A24A, Playfair Display + DM Sans

## Regras de visual
- rodapé: "Daniel Oliveira | Bridge & Co."
- variar o tema da capa entre navy, cream e gold de um dia para o outro (nunca 2 capas iguais seguidas)
- cada post usa pelo menos 2 visuais diferentes (busca, comparação, calendário, checklist, notificação, chat, ícones, número grande, estrelas)
- números só se forem reais ou marcados como exemplo; nada de estatística inventada
- sem logos de terceiros (Google, Instagram, etc.)
