import streamlit as st
from components.navigation import renderizar_menu_superior, cascata_jogadores
from data.queries import obter_perfil_jogador, obter_mapa_arremessos_jogador
from components.charts import grafico_mapa_arremessos

renderizar_menu_superior()
jogador_nome, temporada_selecionada, tipo_temporada = cascata_jogadores()

st.caption("📋 **O que é isto?** Mapeamento físico de onde os lançamentos do jogador ocorrem. Bolinhas verdes são acertos, cruzes vermelhas são erros.")

perfil = obter_perfil_jogador(jogador_nome)
if perfil:
    with st.spinner("Buscando coordenadas dos arremessos..."):
        df_shots = obter_mapa_arremessos_jogador(perfil.get("id"), temporada_selecionada, tipo_temporada)
    
    if not df_shots.empty:
        total_acertos = len(df_shots[df_shots['SHOT_MADE_FLAG'] == 1])
        fg_pct = (total_acertos / len(df_shots)) * 100
        st.markdown(f"**Volume Total:** {len(df_shots)} arremessos | **Aproveitamento Geral:** {fg_pct:.1f}%")
        
        fig = grafico_mapa_arremessos(df_shots)
        if fig: st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})
    else:
        st.info("Nenhum arremesso registado para este recorte.")