import streamlit as st
from data.queries import obter_estatisticas_resumo

st.title("⚡ Impact & Efficiency")

jogador_nome = st.session_state.get('filtro_jogador')
temporada_selecionada = st.session_state.get('filtro_temporada')

if not jogador_nome or jogador_nome == "Selecione um jogador...":
    st.warning("👈 Por favor, selecione um jogador na barra lateral para começar.")
    st.stop()

st.markdown(f"Avaliando o impacto global de **{jogador_nome}** na temporada **{temporada_selecionada}**.")
st.divider()

# Precisamos do ID do jogador para a query de resumo
from data.queries import obter_perfil_jogador
perfil = obter_perfil_jogador(jogador_nome)
jogador_id = perfil.get("id") if perfil else None

stats = obter_estatisticas_resumo(jogador_id, temporada_selecionada)

if stats:
    off_rating = stats.get("off_rating", "N/A")
    def_rating = stats.get("def_rating", "N/A")
    net_rating = stats.get("net_rating", "N/A")
    
    # PIE geralmente vem quebrado (ex: 0.154), multiplicamos por 100
    pie_raw = stats.get("pie")
    pie = f"{round(pie_raw * 100, 1)}%" if pie_raw is not None else "N/A"
    
    pace = round(stats.get("pace", 0), 1) if stats.get("pace") else "N/A"

    st.subheader("Métricas de Quadra (On-Court)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Offensive Rating (ORTG)", 
            value=off_rating, 
            help="Pontos que a equipe marca a cada 100 posses com o jogador em quadra."
        )
    with col2:
        # No Def Rating, quanto menor, melhor. O Streamlit delta inverte a cor com 'inverse'
        st.metric(
            label="Defensive Rating (DRTG)", 
            value=def_rating, 
            help="Pontos que a equipe sofre a cada 100 posses com o jogador em quadra."
        )
    with col3:
        # Se o Net Rating for positivo, ele fica verde automaticamente.
        st.metric(
            label="Net Rating", 
            value=net_rating,
            delta=net_rating if isinstance(net_rating, float) else None,
            delta_color="normal",
            help="A diferença entre o ORTG e o DRTG. Valores positivos indicam que o time vence os minutos deste jogador."
        )

    with st.expander("💡 Como interpretar o Ratings?"):
        st.markdown("""
        - **ORTG / DRTG:** O basquete mede eficiência por posses de bola, não por minutos. Essas métricas mostram o placar da equipe a cada 100 posses de bola enquanto o jogador está jogando.
        - **Net Rating:** É o saldo. Um Net Rating de `+5.0` significa que a equipe ganha do adversário por 5 pontos a cada 100 posses.
        """)

    st.divider()

    st.subheader("Impacto Global")
    col4, col5 = st.columns(2)
    
    with col4:
        st.metric("PIE (Player Impact Estimate)", pie, help="Mede a porcentagem de eventos positivos da partida que foram produzidos por este jogador.")
    with col5:
        st.metric("Pace (Ritmo)", pace, help="Número estimado de posses de bola por 48 minutos. Jogadores com Pace alto jogam em transição rápida.")

    with st.expander("💡 O que é PIE?"):
        st.markdown("""
        O **PIE** é a métrica oficial da NBA para medir o impacto consolidado. 
        Um PIE acima de **10%** significa que o jogador tem uma contribuição acima da média em eventos importantes do jogo (pontos, rebotes, tocos, assistências, menos turnovers). Estrelas costumam operar na casa dos **15% a 20%**.
        """)

else:
    st.error("Dados de impacto indisponíveis para esta temporada.")