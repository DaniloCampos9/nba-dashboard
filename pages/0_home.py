import streamlit as st
from components.navigation import renderizar_menu_superior

renderizar_menu_superior()

# Hero Section
st.markdown("""
<div style='text-align: center; padding: 3rem 0;'>
    <h1 style='font-size: 3.5rem; margin-bottom: 0;'>NBA Advanced Analytics</h1>
    <p style='font-size: 1.2rem; color: #888; max-width: 600px; margin: 10px auto;'>
        Inteligência de basquete levada a sério. Vá além do box-score com rastreamento espacial, 
        arquétipos táticos de IA e métricas de eficiência em um ecossistema fluído.
    </p>
</div>
""", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🚀 Iniciar Análise de Jogadores", use_container_width=True, type="primary"):
        st.switch_page("pages/1_overview.py")

st.divider()

# Value Props (Funcionalidades Explicadas de Forma Simples)
c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("### 🧬 DNA de Jogadores")
        st.markdown("Descubra o **Arquétipo** exato do atleta (ex: *Stretch Big*, *3&D Specialist*). Analise relatórios de *Scouting* gerados por IA e mapas de arremesso interativos.")

with c2:
    with st.container(border=True):
        st.markdown("### 🏢 Raio-X de Franquias")
        st.markdown("Não olhe apenas para vitórias. Entenda o **Pace** (Ritmo de jogo), o saldo de pontos por posse (*Net Rating*) e mergulhe no Depth Chart da rotação de banco.")

with c3:
    with st.container(border=True):
        st.markdown("### ⚔️ Confronto Direto")
        st.markdown("Compare até 3 jogadores lado a lado. Os radares de atributos normalizam as estatísticas para que você compare um armador com um pivô de forma justa.")