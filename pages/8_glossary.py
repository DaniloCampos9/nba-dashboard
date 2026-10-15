import streamlit as st
from components.navigation import renderizar_menu_superior

renderizar_menu_superior()
st.title("📚 Dicionário & Metodologia")
st.markdown("Bem-vindo ao dicionário de métricas do nosso painel. Aqui encontra a definição, fórmula e forma de interpretar cada estatística utilizada no *Basketball Analytics* moderno.")
st.divider()

aba_trad, aba_efi, aba_uso, aba_imp, aba_perimetro = st.tabs([
    "📊 Tradicionais", 
    "🎯 Eficiência", 
    "🧠 Criação", 
    "⚡ Impacto",
    "🏹 Perímetro & Papéis"
])

with aba_trad:
    st.subheader("Estatísticas Tradicionais (Box Score)")
    with st.expander("PPG, RPG, APG (Per Game Stats)", expanded=True):
        st.markdown("""
        **O que mede:** Pontos, Rebotes e Assistências por Jogo.
        - **Como interpretar:** É a produção bruta do jogador. Representa o volume absoluto entregue em média por partida.
        - **Limitações:** Não considera o ritmo (Pace) da equipa nem a eficiência. Um jogador pode ter um PPG alto simplesmente por arremessar muitas vezes e jogar numa equipa que corre muito.
        """)
        
with aba_efi:
    st.subheader("Métricas de Eficiência")
    with st.expander("TS% (True Shooting Percentage)", expanded=True):
        st.markdown("""
        **O que mede:** A eficiência real de pontuação de um jogador.
        - **Fórmula:** `Pontos / (2 * (FGA + 0.44 * FTA))`
        - **Como interpretar:** É a métrica definitiva para avaliar se um jogador arremessa bem. Diferente do FG% (aproveitamento de quadra normal), o TS% dá o peso matemático correto para os arremessos de 3 pontos (que valem mais) e inclui a habilidade de converter lances livres.
        - **Referência:** A média da liga costuma ficar em torno de **57% a 58%**. Estrelas de elite ultrapassam os **62%**.
        """)
    with st.expander("eFG% (Effective Field Goal Percentage)"):
        st.markdown("""
        **O que mede:** O aproveitamento de quadra ajustado para bolas de 3.
        - **Como interpretar:** Parecido com o TS%, mas **não inclui os lances livres**. É excelente para medir quão letal o jogador é exclusivamente com a bola a rolar.
        """)

with aba_uso:
    st.subheader("Criação e Envolvimento")
    with st.expander("USG% (Usage Rate)", expanded=True):
        st.markdown("""
        **O que mede:** A percentagem das posses de bola da equipa que "terminam" nas mãos do jogador enquanto ele está em quadra.
        - **Como interpretar:** Uma posse "termina" com o jogador quando ele arremessa, sofre falta ou comete um turnover. Mostra o peso da responsabilidade ofensiva.
        - **Referência:** Um USG de **20%** é a média exata (1/5 da equipa). Astros de altíssimo volume (como Luka Doncic ou Joel Embiid) operam na casa dos **32% a 38%**.
        """)
    with st.expander("AST% (Assist Percentage)"):
        st.markdown("""
        **O que mede:** A percentagem de arremessos convertidos pelos companheiros que receberam assistência desse jogador.
        - **Como interpretar:** Mostra quão vital o jogador é como distribuidor. Um AST% alto significa que a equipa depende da visão de quadra dele para pontuar.
        """)

with aba_imp:
    st.subheader("Impacto e On/Off")
    with st.expander("ORTG & DRTG (Offensive / Defensive Rating)", expanded=True):
        st.markdown("""
        **O que mede:** Pontos marcados (ORTG) ou sofridos (DRTG) pela equipa a cada **100 posses de bola** com o jogador em quadra.
        - **Como interpretar:** A melhor forma de medir ataques e defesas, pois normaliza o ritmo de jogo.
        """)
    with st.expander("Net Rating"):
        st.markdown("""
        **O que mede:** A diferença entre o ORTG e o DRTG.
        - **Como interpretar:** É o saldo de pontos por 100 posses. Se o Net Rating é de **+6.5**, a equipa "vence" os minutos daquele jogador por uma margem de 6.5 pontos a cada 100 posses.
        """)
    with st.expander("PIE (Player Impact Estimate)"):
        st.markdown("""
        **O que mede:** Métrica oficial da NBA que estima a percentagem de eventos do jogo nos quais o jogador se envolveu positivamente.
        """)
        
with aba_perimetro:
    st.subheader("Métricas de Perímetro e Papéis Táticos")
    with st.expander("3PM, 3PA e 3P% (Volume e Precisão)", expanded=True):
        st.markdown("""
        **O que medem:** Bolas de 3 Convertidas (Made), Tentadas (Attempted) e o Aproveitamento (%).
        - **Como interpretar:** Na NBA moderna, o volume (3PA) é tão importante quanto a precisão. Jogadores que arremessam muito com bom aproveitamento possuem **"Gravidade Ofensiva"**, obrigando a defesa a marcá-los longe do cesto.
        """)
    with st.expander("Arquétipos e Perfis Posicionais"):
        st.markdown("""
        O painel classifica os jogadores combinando volume de uso, impacto defensivo e arremessos de fora para criar definições exatas, tais como:
        - **Stretch Big:** Pivôs que arremessam de 3 pontos, puxando o protetor de aro adversário para fora do garrafão.
        - **3&D Specialist:** Alas que não precisam da bola nas mãos (Baixo USG%), focados em converter tiros de 3 pontos em transição enquanto defendem o melhor jogador adversário.
        - **Franchise Cornerstone:** A âncora da equipa. Jogadores com altíssimo Volume de Uso (USG% > 28) e grande impacto estatístico global (PIE).
        """)