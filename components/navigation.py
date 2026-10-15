import streamlit as st
from data.queries import obter_lista_jogadores, obter_lista_times

def renderizar_menu_superior():
    """Oculta a barra lateral nativa, o cabeçalho do Streamlit e injeta o Menu Principal no topo."""
    st.markdown("""
        <style>
            /* Oculta a barra lateral e o botão de expandir */
            [data-testid="collapsedControl"] { display: none !important; }
            section[data-testid="stSidebar"] { display: none !important; }
            
            /* Oculta o cabeçalho fixo nativo do Streamlit (botão Deploy/Menu) que causa o corte */
            header[data-testid="stHeader"] { display: none !important; }
            
            /* Ajusta as margens para dar o respiro exato ao menu horizontal */
            .block-container { 
                padding-top: 3rem !important; 
                padding-bottom: 2rem !important; 
            }
            
            /* Garante que os ícones e textos do menu se alinham perfeitamente em ecrãs menores */
            div[data-testid="stPageLink-NavLink"] {
                display: flex;
                justify-content: center;
                align-items: center;
            }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    cols[0].page_link("pages/0_home.py", label="Início", icon="🏠")
    cols[1].page_link("pages/1_overview.py", label="Jogadores", icon="👤")
    cols[2].page_link("pages/6_teams.py", label="Franquias", icon="🏀")
    cols[3].page_link("pages/5_comparison.py", label="Comparação", icon="⚔️")
    cols[4].page_link("pages/8_glossary.py", label="Dicionário", icon="📚")
    st.divider()

def cascata_jogadores():
    """Fluxo progressivo para as páginas de Análise de Jogadores."""
    st.subheader("👤 Laboratório de Jogadores")
    st.caption("Siga as etapas abaixo para gerar a análise. Os dados vêm diretamente da base oficial da NBA.")

    lista_jogadores = obter_lista_jogadores()
    jogador_atual = st.session_state.get('filtro_jogador', "Selecione um jogador...")

    # ETAPA 1
    jogador = st.selectbox("🔍 Etapa 1: Pesquise e selecione um atleta", ["Selecione um jogador..."] + lista_jogadores,
                           index=0 if jogador_atual not in lista_jogadores else lista_jogadores.index(jogador_atual) + 1)
    st.session_state['filtro_jogador'] = jogador

    if jogador == "Selecione um jogador...":
        st.info("👆 Selecione um jogador acima para iniciar a análise.")
        st.stop() 

    # ETAPA 2
    st.markdown("<br>", unsafe_allow_html=True)
    modo_atual = st.session_state.get('modo_visao', 'Por Temporada')
    modo = st.radio("⏳ Etapa 2: Qual lente temporal deseja utilizar?", ["Por Temporada", "Carreira (All-Time)"],
                    horizontal=True, index=0 if modo_atual == "Por Temporada" else 1)
    st.session_state['modo_visao'] = modo

    temporada = "Carreira"
    tipo = "Regular Season"

    # ETAPA 3 e 4
    if modo == "Por Temporada":
        c1, c2 = st.columns(2)
        with c1:
            temps = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
            temp_atual = st.session_state.get('filtro_temporada', '2026-27')
            temporada = st.selectbox("📅 Etapa 3: Selecione a Temporada", temps, index=temps.index(temp_atual) if temp_atual in temps else 0)
        with c2:
            tipos = ["Regular Season", "Playoffs", "Regular Season + Playoffs"]
            tipo_atual = st.session_state.get('filtro_tipo_temporada', 'Regular Season')
            tipo = st.selectbox("🏆 Etapa 4: Fase do Torneio", tipos, index=tipos.index(tipo_atual) if tipo_atual in tipos else 0)

        st.session_state['filtro_temporada'] = temporada
        st.session_state['filtro_tipo_temporada'] = tipo
    else:
        st.session_state['filtro_temporada'] = "Carreira"

    st.divider()

    # ETAPA FINAL: Sub-menu de Lentes
    st.markdown(f"**Lentes de Análise para: {jogador}**")
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    sc1.page_link("pages/1_overview.py", label="Visão Geral", icon="📊")
    sc2.page_link("pages/2_offense.py", label="Ataque", icon="🎯")
    sc3.page_link("pages/7_shot_chart.py", label="Shot Chart", icon="🗺️")
    sc4.page_link("pages/3_defense.py", label="Defesa", icon="🛡️")
    sc5.page_link("pages/4_impact.py", label="Impacto", icon="⚡")
    st.markdown("<br>", unsafe_allow_html=True)

    return jogador, temporada, tipo

def cascata_times():
    """Fluxo progressivo para Análise de Times."""
    st.subheader("🏢 Central de Franquias")
    st.caption("Analise o ritmo, a eficiência e a rotação completa do elenco.")

    c1, c2 = st.columns(2)
    with c1:
        temps = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
        temp_atual = st.session_state.get('filtro_temporada', '2026-27')
        temporada = st.selectbox("📅 Etapa 1: Temporada", temps, index=temps.index(temp_atual) if temp_atual in temps else 0)
    with c2:
        tipos = ["Regular Season", "Playoffs", "Regular Season + Playoffs"]
        tipo_atual = st.session_state.get('filtro_tipo_temporada', 'Regular Season')
        tipo = st.selectbox("🏆 Etapa 2: Fase do Torneio", tipos, index=tipos.index(tipo_atual) if tipo_atual in tipos else 0)

    st.session_state['filtro_temporada'] = temporada
    st.session_state['filtro_tipo_temporada'] = tipo

    lista_times = obter_lista_times(temporada)
    time_atual = st.session_state.get('filtro_time', "Selecione um time...")
    time_selecionado = st.selectbox("🏀 Etapa 3: Selecione a Franquia", ["Selecione um time..."] + lista_times, 
                                    index=0 if time_atual not in lista_times else lista_times.index(time_atual) + 1)
    st.session_state['filtro_time'] = time_selecionado

    if time_selecionado == "Selecione um time...":
        st.info("👆 Selecione uma franquia acima para carregar o Depth Chart e o Scouting Report.")
        st.stop()

    st.divider()
    return time_selecionado, temporada, tipo