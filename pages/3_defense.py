import streamlit as st
from data.queries import obter_perfil_jogador, obter_estatisticas_resumo, obter_estatisticas_defesa

st.title("🛡️ Defensive Profile")

jogador_nome = st.session_state.get('filtro_jogador')
temporada_selecionada = st.session_state.get('filtro_temporada')

if not jogador_nome or jogador_nome == "Selecione um jogador...":
    st.warning("👈 Por favor, selecione um jogador na barra lateral para começar.")
    st.stop()

st.markdown(f"Métricas de esforço (Hustle) e impacto defensivo de **{jogador_nome}** na temporada **{temporada_selecionada}**.")
st.divider()

perfil = obter_perfil_jogador(jogador_nome)
jogador_id = perfil.get("id") if perfil else None

# Puxamos os dados gerais (para saber quantos jogos ele disputou) e os de defesa
stats_gerais = obter_estatisticas_resumo(jogador_id, temporada_selecionada)
stats_defesa = obter_estatisticas_defesa(jogador_id, temporada_selecionada)

if stats_defesa and stats_gerais:
    jogos = stats_gerais.get("jogos_disputados", 0)
    
    if jogos > 0:
        # Calculando as médias por jogo (Per Game)
        spg = round(stats_defesa.get("roubos_totais", 0) / jogos, 1)
        bpg = round(stats_defesa.get("tocos_totais", 0) / jogos, 1)
        deflections = round(stats_defesa.get("deflections", 0) / jogos, 1)
        
        # O Def Rating a gente puxa da tabela avançada (já estava no stats_gerais)
        def_rating = stats_gerais.get("def_rating", "N/A")
        
        st.subheader("Atividade Defensiva (Per Game)")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Steals (Roubos)", spg, help="Roubos de bola por jogo.")
        with col2:
            st.metric("Blocks (Tocos)", bpg, help="Tocos por jogo.")
        with col3:
            st.metric("Deflections", deflections, help="Desvios de bola. Mede o quão ativo o jogador é com as mãos em linhas de passe ou contestando dribles.")
        with col4:
            st.metric("Defensive Rating", def_rating, help="Pontos sofridos pelo time a cada 100 posses com ele em quadra. Quanto menor, melhor.")
            
        st.divider()
        
        # Contexto Analítico
        st.subheader("💡 O que a análise de vídeo e Hustle nos diz:")
        if deflections >= 3.0:
            st.success("Este jogador é um **pesadelo nas linhas de passe**. Uma média de mais de 3 deflections por jogo indica elite no quesito de esforço defensivo (Hustle) e antecipação.")
        elif deflections >= 1.5:
            st.info("O jogador apresenta uma **atividade defensiva sólida** e usa bem a envergadura para desviar posses de bola do adversário.")
        else:
            st.warning("O volume de *deflections* é baixo. Isso pode indicar uma defesa de menor impacto direto na bola (ou uma função de proteção de aro clássica, no caso de pivôs puros).")

        st.markdown("""
        **Nota sobre análise de defesa:** 
        Métricas defensivas em banco de dados são notoriamente incompletas. Roubos e tocos não mostram contestação de arremessos, rotações corretas ou posicionamento (ajudas defensivas). Um jogador com pouco volume aqui ainda pode ser um excelente defensor de sistema.
        """)
        
    else:
        st.warning("O jogador ainda não disputou partidas nesta temporada.")
else:
    st.error(f"Dados defensivos indisponíveis para a temporada {temporada_selecionada}.")