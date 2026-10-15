import streamlit as st
from components.navigation import renderizar_menu_superior, cascata_jogadores
from data.queries import obter_dados_graficos_ataque
from components.charts import grafico_scatter_ataque

renderizar_menu_superior()
jogador_nome, temporada_selecionada, tipo_temporada = cascata_jogadores()

st.caption("📋 **O que é esta página?** Compara o volume de pontos com a real eficiência (True Shooting) de todos os jogadores ativos da temporada.")

df_graficos = obter_dados_graficos_ataque(temporada_selecionada, tipo_temporada)

if not df_graficos.empty:
    df_graficos = df_graficos[df_graficos['jogos_disputados'] >= 10] 
    col1, col2 = st.columns(2)

    with col1:
        fig1 = grafico_scatter_ataque(df_graficos, "USG%", "TS%", "Volume vs Eficiência", "Usage Rate (USG%) × True Shooting (TS%)", jogador_nome)
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        with st.expander("💡 Como interpretar?"):
            st.markdown("Jogadores à **direita** usam mais posses. Mais **acima** significa maior eficiência no arremesso.")

    with col2:
        fig2 = grafico_scatter_ataque(df_graficos, "PPG", "TS%", "Produção vs Eficiência", "Pontos por Jogo (PPG) × True Shooting (TS%)", jogador_nome)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        with st.expander("💡 Como interpretar?"):
            st.markdown("O quadrante **superior direito** representa a elite absoluta de pontuação da liga.")