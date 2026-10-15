import streamlit as st
from components.navigation import renderizar_menu_superior, cascata_jogadores
from data.queries import obter_estatisticas_resumo, obter_perfil_jogador

renderizar_menu_superior()
jogador_nome, temporada_selecionada, tipo_temporada = cascata_jogadores()

st.caption("📋 **O que é esta página?** Mostra se a equipa ganha ou perde o jogo durante os minutos em que este jogador está na quadra (Ratings e PIE).")

perfil = obter_perfil_jogador(jogador_nome)
jogador_id = perfil.get("id") if perfil else None
stats = obter_estatisticas_resumo(jogador_id, temporada_selecionada, tipo_temporada)

if stats:
    off_rating = round(stats.get("off_rating", 0), 1)
    def_rating = round(stats.get("def_rating", 0), 1)
    net_rating = round(stats.get("net_rating", 0), 1)
    pie = f"{round((stats.get('pie') or 0) * 100, 1)}%"
    pace = round(stats.get("pace", 0), 1)

    c1, c2, c3 = st.columns(3)
    c1.metric("Offensive Rating", off_rating, help="Pontos a favor por 100 posses.")
    c2.metric("Defensive Rating", def_rating, help="Pontos contra por 100 posses.")
    c3.metric("Net Rating", net_rating, delta=net_rating, delta_color="normal", help="O saldo. Positivo significa que a equipa vence com ele.")

    c4, c5 = st.columns(2)
    c4.metric("PIE (Impacto Global)", pie, help="Mede a % de contribuição direta para as coisas boas que acontecem no jogo.")
    c5.metric("Pace (Ritmo)", pace, help="Estimativa de posses de bola por jogo.")