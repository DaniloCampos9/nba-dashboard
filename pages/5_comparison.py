import streamlit as st
import pandas as pd
from data.queries import obter_lista_jogadores, obter_perfil_jogador, obter_estatisticas_resumo
import plotly.graph_objects as go

st.title("⚔️ Player Comparison")
st.markdown("Compare até 3 jogadores ou diferentes versões do mesmo jogador ao longo dos anos e torneios.")
st.divider()

lista_jogadores = obter_lista_jogadores()
temporadas = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
# 👇 1. Criamos a lista de opções de tipo de temporada para essa tela
tipos_temporada = ["Regular Season", "Playoffs", "Regular Season + Playoffs"]

# Cria 3 colunas para a seleção
col_sel1, col_sel2, col_sel3 = st.columns(3)

# Dicionário para guardar as escolhas e resultados
comparacao = {}

def renderizar_seletor(col, num_card):
    with col:
        st.subheader(f"Opção {num_card}")
        jog = st.selectbox(f"Jogador {num_card}", ["Nenhum"] + lista_jogadores, key=f"jog_{num_card}")
        temp = st.selectbox(f"Temporada {num_card}", temporadas, key=f"temp_{num_card}")
        # 👇 2. Adicionamos a caixa de seleção do Tipo dentro do card do jogador
        tipo = st.selectbox(f"Tipo {num_card}", tipos_temporada, key=f"tipo_{num_card}")
        
        if jog != "Nenhum":
            perfil = obter_perfil_jogador(jog)
            if perfil:
                # 👇 3. Passamos a nova variável 'tipo' para a função do banco
                stats = obter_estatisticas_resumo(perfil['id'], temp, tipo)
                if stats:
                    # 👉 Atualizamos o nome para indicar se é (Reg) ou (Play) no título
                    sigla = "RS" if tipo == "Regular Season" else "PO" if tipo == "Playoffs" else "ALL"
                    return {"nome": f"{jog} ({temp[-2:]} {sigla})", "stats": stats, "perfil": perfil}
                else:
                    st.warning(f"Sem dados para {temp} ({tipo})")
        return None

# Renderiza os menus e coleta os dados se existirem
atleta1 = renderizar_seletor(col_sel1, 1)
atleta2 = renderizar_seletor(col_sel2, 2)
atleta3 = renderizar_seletor(col_sel3, 3)

atletas_validos = [a for a in [atleta1, atleta2, atleta3] if a is not None]

st.divider()

if len(atletas_validos) > 0:
    st.subheader("📊 Confronto Estatístico")
    
    # Prepara os dados para a tabela
    tabela_comparativa = []
    
    for a in atletas_validos:
        stats = a["stats"]
        jogos = stats.get("jogos_disputados", 1)
        if jogos == 0: jogos = 1
        
        # Pega as fotos pra ficar estiloso
        url_foto = f"https://cdn.nba.com/headshots/nba/latest/254x190/{a['perfil']['id']}.png"
        
        # 👇 Adicionamos arredondamento de casa decimal ao Net Rating
        net_rating_raw = stats.get("net_rating", 0)
        net_rating = round(net_rating_raw, 1) if isinstance(net_rating_raw, float) else net_rating_raw
        
        tabela_comparativa.append({
            "Foto": url_foto, 
            "Atleta": a["nome"],
            "Jogos": stats.get("jogos_disputados", 0),
            "PPG": round(stats.get("pontos_totais", 0) / jogos, 1),
            "RPG": round(stats.get("rebotes_totais", 0) / jogos, 1),
            "APG": round(stats.get("assistencias_totais", 0) / jogos, 1),
            "TS%": f"{round(stats.get('ts_pct', 0) * 100, 1)}%",
            "USG%": f"{round(stats.get('usg_pct', 0) * 100, 1)}%",
            "Net Rating": net_rating
        })
    
    # Converte para Pandas e transpõe para os jogadores ficarem nas colunas
    df_comp = pd.DataFrame(tabela_comparativa).set_index("Atleta").T
    
    # Remove a linha da URL da foto do Dataframe que será renderizado
    df_exibicao = df_comp.drop("Foto")
    
    # Mostramos os rostos primeiro
    col_fotos = st.columns(len(atletas_validos))
    for i, col in enumerate(col_fotos):
        with col:
            st.image(tabela_comparativa[i]["Foto"], width=120)
            st.markdown(f"**{tabela_comparativa[i]['Atleta']}**")
    
    # Exibe a tabela transposta
    st.dataframe(df_exibicao, use_container_width=True)

    # Gráfico de Barras Agrupadas para Produção (PPG, RPG, APG)
    st.subheader("Produção Bruta (Per Game)")
    
    fig = go.Figure()
    metrics = ['PPG', 'RPG', 'APG']
    
    for a in tabela_comparativa:
        valores = [a[m] for m in metrics]
        fig.add_trace(go.Bar(name=a["Atleta"], x=metrics, y=valores))
        
    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA')
    )
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Selecione pelo menos um jogador acima para iniciar a comparação.")