import streamlit as st
from data.queries import obter_dados_graficos_ataque
from components.charts import grafico_scatter_ataque

st.title("🎯 Offensive Profile")

jogador_nome = st.session_state.get('filtro_jogador')
temporada_selecionada = st.session_state.get('filtro_temporada')
# 👇 1. Resgatando o tipo de temporada
tipo_temporada = st.session_state.get('filtro_tipo_temporada', 'Regular Season')

if not jogador_nome or jogador_nome == "Selecione um jogador...":
    st.warning("👈 Por favor, selecione um jogador na barra lateral para começar.")
    st.stop()

# 👇 2. Adicionando o tipo de temporada no contexto visual
st.markdown(f"Analisando a produção e eficiência de **{jogador_nome}** na temporada **{temporada_selecionada}** ({tipo_temporada}).")
st.divider()

# 👇 3. Passando a flag para a função da API do banco
df_graficos = obter_dados_graficos_ataque(temporada_selecionada, tipo_temporada)

if not df_graficos.empty:
    # Filtro básico: Esconde jogadores com menos de 10 jogos para não quebrar o gráfico com anomalias (ex: cara que jogou 2 min, fez 2 pontos e tem 100% de TS%)
    df_graficos = df_graficos[df_graficos['jogos_disputados'] >= 10] 

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico 1: Volume x Eficiência
        fig1 = grafico_scatter_ataque(
            df=df_graficos,
            x_col="USG%",
            y_col="TS%",
            titulo="Volume vs Eficiência",
            subtitulo="Usage Rate (USG%) × True Shooting (TS%)",
            jogador_destaque=jogador_nome
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        
        # O expander explicativo do PRD
        with st.expander("💡 Como interpretar?"):
            st.markdown("Jogadores mais à **direita** utilizam maior volume de posses do time. Jogadores mais **acima** possuem maior eficiência de pontuação.")

    with col2:
        # Gráfico 2: Produção x Eficiência
        fig2 = grafico_scatter_ataque(
            df=df_graficos,
            x_col="PPG",
            y_col="TS%",
            titulo="Produção vs Eficiência",
            subtitulo="Pontos por Jogo (PPG) × True Shooting (TS%)",
            jogador_destaque=jogador_nome
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        
        with st.expander("💡 Como interpretar?"):
            st.markdown("Mostra produção e eficiência simultaneamente. O quadrante **superior direito** representa a elite da liga.")

else:
    st.error("Não foi possível carregar os dados para os gráficos.")