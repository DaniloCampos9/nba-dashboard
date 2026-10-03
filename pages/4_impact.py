import streamlit as st
from data.queries import obter_estatisticas_resumo, obter_perfil_jogador

st.title("⚡ Impact & Efficiency")

jogador_nome = st.session_state.get('filtro_jogador')
temporada_selecionada = st.session_state.get('filtro_temporada')
# 👇 1. Resgatando o tipo de temporada
tipo_temporada = st.session_state.get('filtro_tipo_temporada', 'Regular Season')

if not jogador_nome or jogador_nome == "Selecione um jogador...":
    st.warning("👈 Por favor, selecione um jogador na barra lateral para começar.")
    st.stop()

# 👇 2. Mostrando a flag na tela
st.markdown(f"Avaliando o impacto global de **{jogador_nome}** na temporada **{temporada_selecionada}** ({tipo_temporada}).")
st.divider()

perfil = obter_perfil_jogador(jogador_nome)
jogador_id = perfil.get("id") if perfil else None

# 👇 3. Passando a flag para o banco de dados
stats = obter_estatisticas_resumo(jogador_id, temporada_selecionada, tipo_temporada)

if stats:
    off_rating = stats.get("off_rating", "N/A")
    if isinstance(off_rating, float): off_rating = round(off_rating, 1)
    
    def_rating = stats.get("def_rating", "N/A")
    if isinstance(def_rating, float): def_rating = round(def_rating, 1)
    
    net_rating = stats.get("net_rating", "N/A")
    if isinstance(net_rating, float): net_rating = round(net_rating, 1)
    
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
        st.metric(
            label="Defensive Rating (DRTG)", 
            value=def_rating, 
            help="Pontos que a equipe sofre a cada 100 posses com o jogador em quadra."
        )
    with col3:
        st.metric(
            label="Net Rating", 
            value=net_rating,
            delta=net_rating if isinstance(net_rating, (float, int)) else None,
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