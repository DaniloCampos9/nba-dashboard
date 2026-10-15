import streamlit as st
from components.navigation import renderizar_menu_superior, cascata_jogadores
from data.queries import obter_perfil_jogador, obter_estatisticas_resumo, obter_estatisticas_defesa

renderizar_menu_superior()
jogador_nome, temporada_selecionada, tipo_temporada = cascata_jogadores()

st.caption("📋 **O que é esta página?** Mede o esforço (Hustle) e as estatísticas de defesa puras (Tocos/Roubos) do atleta.")

perfil = obter_perfil_jogador(jogador_nome)
jogador_id = perfil.get("id") if perfil else None

stats_gerais = obter_estatisticas_resumo(jogador_id, temporada_selecionada, tipo_temporada)
stats_defesa = obter_estatisticas_defesa(jogador_id, temporada_selecionada, tipo_temporada)

if stats_defesa and stats_gerais:
    jogos = stats_gerais.get("jogos_disputados", 0)
    if jogos > 0:
        spg = round(stats_defesa.get("roubos_totais", 0) / jogos, 1)
        bpg = round(stats_defesa.get("tocos_totais", 0) / jogos, 1)
        deflections = round(stats_defesa.get("deflections", 0) / jogos, 1)
        def_rating = round(stats_gerais.get("def_rating", 0), 1)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Steals (Roubos)", spg, help="Roubos de bola por jogo.")
        col2.metric("Blocks (Tocos)", bpg, help="Tocos por jogo.")
        col3.metric("Deflections", deflections, help="Vezes que o jogador desvia passes do adversário por jogo.")
        col4.metric("Defensive Rating", def_rating, help="Pontos sofridos a cada 100 posses em quadra.")
        
        st.divider()
        st.subheader("💡 Conclusões de Esforço e Marcação:")
        if deflections >= 3.0: st.success("Este jogador é um **pesadelo nas linhas de passe** (Elite em deflections).")
        elif deflections >= 1.5: st.info("Apresenta **atividade defensiva sólida**, usando bem as mãos para incomodar.")
        else: st.warning("Baixo volume de desvios, indicando um papel de contenção menos agressivo na bola.")