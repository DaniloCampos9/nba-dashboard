import streamlit as st

st.title("🏀 NBA Advanced Analytics Hub")
st.markdown("### Bem-vindo à plataforma definitiva de inteligência, tracking e estatísticas avançadas da NBA.")
st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    Esta aplicação foi desenvolvida sob rigorosos padrões de **Engenharia de Dados e Análise Esportiva**, integrando dados oficiais da NBA API e Supabase para entregar insights profundos que vão muito além do box-score tradicional.
    
    ### 🚀 O que você encontra por aqui:
    * **📊 Overview & Player Snapshot:** Cartões de KPIs avançados (True Shooting, Usage Rate, Net Rating, PIE), **Arquétipos Estilo NBA 2K**, feed de notícias em tempo real e linha do tempo completa de carreira com logotipos das franquias.
    * **🎯 Offensive & Defensive Profiles:** Gráficos de dispersão de volume e eficiência, além de métricas de esforço (*Hustle* e *Deflections*).
    * **🗺️ Shot Charts:** Mapeamento espacial interativo de arremessos em quadra.
    * **⚔️ Player Comparison:** Confronto direto entre até 3 atletas ou versões históricas de um mesmo jogador (incluindo Playoffs).
    * **🏀 Team Analytics:** Análise de sistema, ritmo (*Pace*) e quadrantes de eficiência da liga (*Contenders*, *Tiroteio*, *Trincheira* e *Loteria*).
    """)

with col2:
    st.info("""
    👈 **Como Começar:**
    
    1. Vá até a **barra lateral** à esquerda.
    2. Selecione a **Temporada** desejada.
    3. Escolha o **Tipo de Temporada** (Regular Season, Playoffs ou Ambos).
    4. Selecione o **Jogador** que deseja analisar.
    
    Explore todas as abas no menu superior!
    """)

st.divider()
st.markdown("*(Dica: Selecione um atleta na barra lateral e clique na aba **Overview** no menu superior para iniciar sua imersão analítica.)*")