import streamlit as st

st.title("📚 Glossário & Metodologia")
st.markdown("Bem-vindo ao dicionário de métricas do nosso painel. Aqui você encontra a definição, fórmula e forma de interpretar cada estatística utilizada no Basketball Analytics moderno.")
st.divider()

# Criando abas para organizar por categorias
aba_trad, aba_efi, aba_uso, aba_imp = st.tabs([
    "📊 Tradicionais", 
    "🎯 Eficiência", 
    "🧠 Criação e Envolvimento", 
    "⚡ Impacto (Avançadas)"
])

with aba_trad:
    st.subheader("Estatísticas Tradicionais (Box Score)")
    
    with st.expander("PPG, RPG, APG (Per Game Stats)", expanded=True):
        st.markdown("""
        **O que mede:** Pontos, Rebotes e Assistências por Jogo.
        - **Como interpretar:** É a produção bruta do jogador. Representa o volume absoluto entregue em média por partida.
        - **Limitações:** Não considera o ritmo (Pace) da equipe nem a eficiência. Um jogador pode ter um PPG alto simplesmente por arremessar muitas vezes e jogar em um time que corre muito.
        """)
        
with aba_efi:
    st.subheader("Métricas de Eficiência")
    
    with st.expander("TS% (True Shooting Percentage)", expanded=True):
        st.markdown("""
        **O que mede:** A eficiência real de pontuação de um jogador.
        - **Fórmula:** `Pontos / (2 * (FGA + 0.44 * FTA))`
        - **Como interpretar:** É a métrica definitiva para avaliar se um jogador arremessa bem. Diferente do FG% (aproveitamento de quadra normal), o TS% dá o peso matemático correto para as bolas de 3 pontos (que valem mais) e inclui a habilidade de cavar e converter lances livres.
        - **Referência:** A média da liga costuma ficar em torno de **57 porcento a 58%**. Estrelas de elite ultrapassam os **62%**.
        """)
        
    with st.expander("eFG% (Effective Field Goal Percentage)"):
        st.markdown("""
        **O que mede:** O aproveitamento de quadra ajustado para bolas de 3.
        - **Como interpretar:** Parecido com o TS%, mas **não inclui os lances livres**. É excelente para medir quão letal o jogador é exclusivamente com a bola rolando.
        """)

with aba_uso:
    st.subheader("Criação e Envolvimento")
    
    with st.expander("USG% (Usage Rate)", expanded=True):
        st.markdown("""
        **O que mede:** A porcentagem das posses de bola da equipe que "terminam" nas mãos do jogador enquanto ele está em quadra.
        - **Como interpretar:** Uma posse "termina" com o jogador quando ele arremessa, sofre falta para ir ao lance livre ou comete um turnover. Mostra o peso da responsabilidade ofensiva.
        - **Referência:** Um USG de **20%** é a média exata (1/5 do time). Astros de altíssimo volume (como Luka Doncic ou Joel Embiid) operam na casa dos **32% a 38%**.
        """)
        
    with st.expander("AST% (Assist Percentage)"):
        st.markdown("""
        **O que mede:** A porcentagem de arremessos convertidos pelos companheiros de equipe que receberam assistência desse jogador.
        - **Como interpretar:** Mostra o quão vital o jogador é como garçom. Um AST% alto significa que o time depende da visão de quadra dele para pontuar.
        """)

with aba_imp:
    st.subheader("Impacto e On/Off")
    
    with st.expander("ORTG & DRTG (Offensive / Defensive Rating)", expanded=True):
        st.markdown("""
        **O que mede:** Pontos marcados (ORTG) ou sofridos (DRTG) pela equipe a cada **100 posses de bola** com o jogador em quadra.
        - **Como interpretar:** A melhor forma de medir ataques e defesas, pois normaliza o ritmo de jogo. Times mais rápidos têm mais posses e fariam mais pontos naturalmente, os *Ratings* nivelam isso para sabermos quem é realmente mais eficiente. 
        """)
        
    with st.expander("Net Rating"):
        st.markdown("""
        **O que mede:** A diferença entre o ORTG e o DRTG.
        - **Como interpretar:** É o saldo de pontos por 100 posses. Se o Net Rating é de **+6.5**, o time "vence" os minutos daquele jogador por uma margem de 6.5 pontos a cada 100 posses.
        """)
        
    with st.expander("PIE (Player Impact Estimate)"):
        st.markdown("""
        **O que mede:** Métrica oficial da NBA que estima a porcentagem de eventos do jogo nos quais o jogador se envolveu positivamente.
        - **Como interpretar:** Uma "nota geral" de impacto estatístico cru na partida. Leva em conta pontos, tocos, rebotes e pune turnovers e erros.
        """)
        
    with aba_perimetro:
        st.subheader("Métricas de Perímetro e Papéis Táticos")
    
    with st.expander("3PM, 3PA e 3P% (Volume e Precisão)", expanded=True):
        st.markdown("""
        **O que medem:** Bolas de 3 Convertidas (Made), Tentadas (Attempted) e o Aproveitamento (%).
        - **Como interpretar:** Na NBA moderna, o volume (3PA) é tão importante quanto a precisão. Jogadores que arremessam mais de 6 vezes por jogo com um aproveitamento acima de 37% possuem **"Gravidade Ofensiva"**, obrigando a defesa a marcá-los longe da cesta e abrindo espaço para infiltrações do resto do time.
        """)
        
    with st.expander("Arquétipos e Perfis Posicionais"):
        st.markdown("""
        O painel classifica os jogadores combinando volume de uso, impacto defensivo e arremessos de fora para criar definições exatas de seu papel, tais como:
        - **Stretch Big:** Pivôs que arremessam bolas de 3 pontos, puxando o protetor de aro adversário para fora do garrafão.
        - **3&D Specialist:** Alas que não precisam da bola nas mãos (Baixo USG%), focados em converter tiros de 3 pontos em transição ou passes de astros, enquanto defendem o melhor jogador adversário.
        - **Franchise Cornerstone:** A âncora da equipe. Jogadores com altíssimo Volume de Uso (USG% > 28) e grande impacto estatístico global (PIE).
        """)