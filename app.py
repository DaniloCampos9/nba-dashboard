import streamlit as st

st.set_page_config(
    page_title="NBA Player Analytics",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

pages = {
    "Navegação": [
        st.Page("pages/0_home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/1_overview.py", title="Visão Geral", icon="📊"),
        st.Page("pages/2_offense.py", title="Ataque", icon="🎯"),
        st.Page("pages/3_defense.py", title="Defesa", icon="🛡"),
        st.Page("pages/4_impact.py", title="Impacto", icon="⚡"),
        st.Page("pages/7_shot_chart.py", title="Shot Charts", icon="🗺️"),
        st.Page("pages/6_teams.py", title="Times", icon="🏀"),
        st.Page("pages/5_comparison.py", title="Comparação", icon="⚔️"),
        st.Page("pages/8_glossary.py", title="Dicionário", icon="📚")
    ]
}

pg = st.navigation(pages, position="hidden")
pg.run()