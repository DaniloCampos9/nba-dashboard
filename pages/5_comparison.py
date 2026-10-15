import streamlit as st
import pandas as pd
from components.navigation import renderizar_menu_superior
from data.queries import obter_lista_jogadores, obter_perfil_jogador, obter_estatisticas_resumo
import plotly.graph_objects as go
from components.charts import grafico_radar_comparativo

renderizar_menu_superior()
st.subheader("⚔️ Confronto Direto")
st.caption("📋 **Como usar:** Selecione um jogador. Após selecionado, abrirá o espaço para escolher o próximo, até ao máximo de 3 atletas.")

lista_jogadores = obter_lista_jogadores()
temporadas = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
tipos_temporada = ["Regular Season", "Playoffs", "Regular Season + Playoffs"]

def renderizar_seletor(num_card):
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        jog = col1.selectbox(f"Pesquisar Atleta {num_card}", ["Nenhum"] + lista_jogadores, key=f"jog_{num_card}")
        if jog == "Nenhum": return None
        
        temp = col2.selectbox(f"Temporada", temporadas, key=f"temp_{num_card}")
        tipo = col3.selectbox(f"Torneio", tipos_temporada, key=f"tipo_{num_card}")
        
        perfil = obter_perfil_jogador(jog)
        stats = obter_estatisticas_resumo(perfil['id'], temp, tipo) if perfil else None
        if stats: return {"nome": f"{jog} ({temp[-2:]})", "stats": stats, "perfil": perfil}
        return None

# Divulgação Progressiva
atleta1 = renderizar_seletor(1)
atleta2 = renderizar_seletor(2) if atleta1 else None
atleta3 = renderizar_seletor(3) if atleta2 else None

atletas_validos = [a for a in [atleta1, atleta2, atleta3] if a is not None]

if len(atletas_validos) > 0:
    st.divider()
    tabela_comparativa = []
    for a in atletas_validos:
        stats, jogos = a["stats"], max(a["stats"].get("jogos_disputados", 1), 1)
        tabela_comparativa.append({
            "Foto": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{a['perfil']['id']}.png", 
            "Atleta": a["nome"], "Jogos": jogos,
            "PPG": round(stats.get("pontos_totais", 0) / jogos, 1),
            "RPG": round(stats.get("rebotes_totais", 0) / jogos, 1),
            "APG": round(stats.get("assistencias_totais", 0) / jogos, 1),
            "TS%": f"{round(stats.get('ts_pct', 0) * 100, 1)}%",
            "Net Rating": round(stats.get("net_rating", 0), 1)
        })
    
    df_exibicao = pd.DataFrame(tabela_comparativa).set_index("Atleta").T.drop("Foto").astype(str)
    col_fotos = st.columns(len(atletas_validos))
    for i, col in enumerate(col_fotos):
        with col:
            st.image(tabela_comparativa[i]["Foto"], width=120)
            st.markdown(f"**{tabela_comparativa[i]['Atleta']}**")
    st.dataframe(df_exibicao, use_container_width=True)

    col_radar, col_barras = st.columns(2)
    with col_radar:
        fig_radar = grafico_radar_comparativo(atletas_validos)
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})