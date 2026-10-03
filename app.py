import streamlit as st
from data.queries import obter_lista_jogadores

# 1. Configuração da página DEVE ser o primeiro comando
st.set_page_config(
    page_title="NBA Player Analytics",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Configuração dos Filtros Globais na Sidebar
st.sidebar.title("⚙️ Filtros da Análise")

temporadas_disponiveis = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
temporada = st.sidebar.selectbox("Temporada", temporadas_disponiveis, index=0)
tipo_temporada = st.sidebar.radio("Tipo de Temporada", ["Regular Season", "Playoffs", "Regular Season + Playoffs"])

st.sidebar.divider()
st.sidebar.markdown("### Contexto do Jogador")

# A MÁGICA ACONTECE AQUI: Adicionamos um placeholder inicial para o usuário escolher o jogador
lista_jogadores = obter_lista_jogadores()
opcoes_jogadores = ["Selecione um jogador..."] + lista_jogadores
jogador_selecionado = st.sidebar.selectbox("Jogador", opcoes_jogadores)

# Salvar filtros na sessão para as outras páginas lerem
st.session_state['filtro_temporada'] = temporada
st.session_state['filtro_tipo_temporada'] = tipo_temporada
st.session_state['filtro_jogador'] = jogador_selecionado

# 3. Roteamento de Páginas (Home configurada como padrão)
pages = {
    "Início": [
        st.Page("pages/0_home.py", title="Home / Bem-vindo", icon="🏠", default=True),
    ],
    "Dashboard": [
        st.Page("pages/1_overview.py", title="Overview", icon="📊"),
        st.Page("pages/2_offense.py", title="Offensive Profile", icon="🎯"),
        st.Page("pages/7_shot_chart.py", title="Shot Charts", icon="🗺️"), 
        st.Page("pages/3_defense.py", title="Defensive Profile", icon="🛡"),
        st.Page("pages/4_impact.py", title="Impact & Efficiency", icon="⚡"),
        st.Page("pages/6_teams.py", title="Team Analytics", icon="🏀"),
    ],
    "Ferramentas": [
        st.Page("pages/5_comparison.py", title="Player Comparison", icon="⚔️")
    ],
    "Metodologia": [
        st.Page("pages/8_glossary.py", title="Glossary & Methodology", icon="📚")
    ]
}

pg = st.navigation(pages)
pg.run()