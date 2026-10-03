import streamlit as st
from data.queries import obter_perfil_jogador, obter_mapa_arremessos_jogador
from components.charts import grafico_mapa_arremessos

st.title("🗺️ Mapa de Arremessos (Shot Chart)")
st.markdown("Visualização espacial da eficiência de pontuação. Cada ponto representa um arremesso tentado.")

jogador_nome = st.session_state.get('filtro_jogador')
temporada_selecionada = st.session_state.get('filtro_temporada')
# 👇 1. Resgatando o tipo de temporada da sessão
tipo_temporada = st.session_state.get('filtro_tipo_temporada', 'Regular Season')

if not jogador_nome:
    st.warning("Selecione um jogador na barra lateral.")
    st.stop()

perfil = obter_perfil_jogador(jogador_nome)
if perfil:
    jogador_id = perfil.get("id")
    
    # 👇 2. Atualizando o texto de carregamento para refletir o filtro
    with st.spinner(f"Buscando histórico de arremessos de {jogador_nome} ({tipo_temporada})..."):
        # 👇 3. Passando a flag para a requisição da API
        df_shots = obter_mapa_arremessos_jogador(jogador_id, temporada_selecionada, tipo_temporada)
    
    if not df_shots.empty:
        total_acertos = len(df_shots[df_shots['SHOT_MADE_FLAG'] == 1])
        total_tentativas = len(df_shots)
        fg_pct = (total_acertos / total_tentativas) * 100
        
        # 👇 4. Mostrando a flag no título do gráfico
        st.markdown(f"### {jogador_nome} - {temporada_selecionada} ({tipo_temporada})")
        st.caption(f"**Volume Total:** {total_tentativas} arremessos | **Aproveitamento Geral:** {fg_pct:.1f}%")
        
        # Chama a função mágica do Plotly
        fig = grafico_mapa_arremessos(df_shots)
        if fig:
            # O config scrollZoom=False impede que o mapa perca o enquadramento sem querer
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})
    else:
        st.info(f"Nenhum dado de arremesso encontrado para {jogador_nome} nesta temporada ({tipo_temporada}).")