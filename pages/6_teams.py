import streamlit as st
import pandas as pd
from components.navigation import renderizar_menu_superior, cascata_times
from data.queries import obter_identidade_time, obter_elenco_time

renderizar_menu_superior()
time_selecionado, temporada, tipo_temporada = cascata_times()

st.caption("📋 **O que é isto?** Avalia a identidade ofensiva/defensiva da equipa como um coletivo e expõe os minutos e funções da rotação (Depth Chart).")

# 👇 UX MELHORADA: O Spinner informa o utilizador que o sistema está a trabalhar
with st.spinner(f"A montar o Raio-X tático e a carregar o elenco de {time_selecionado}..."):
    dados_time = obter_identidade_time(time_selecionado, temporada, tipo_temporada)
    df_elenco = obter_elenco_time(time_selecionado, temporada, tipo_temporada)

if dados_time:
    st.subheader("Eficiência e Ritmo")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Offensive Rating", f"{dados_time.get('off_rating', 0):.1f}")
    col2.metric("Defensive Rating", f"{dados_time.get('def_rating', 0):.1f}", delta_color="inverse")
    col3.metric("Net Rating", f"{dados_time.get('net_rating', 0):.1f}")
    col4.metric("Pace", f"{dados_time.get('pace', 0):.1f}")

    st.markdown("### 🧬 Perfil e Estilo de Jogo")
    
    estilos = []
    pace = dados_time.get('pace', 0)
    
    if pace > 100.5:
        estilos.append("**Pace & Space / Transição Rápida:** A equipa atua num dos ritmos mais acelerados da liga, procurando definir as jogadas rapidamente antes da defesa adversária se estabelecer.")
    elif 0 < pace < 98:
        estilos.append("**Meia-Quadra Metódico:** A equipa opera num ritmo cadenciado, priorizando a execução tática de meia-quadra e reduzindo o número total de posses no jogo.")
    
    net_rtg = dados_time.get('net_rating', 0)
    if net_rtg > 4.5:
        estilos.append("**Dominância Sustentável:** O Net Rating indica um perfil de *Contender* real, vencendo os seus minutos de forma contundente e consistente.")
    elif net_rtg < -4:
        estilos.append("**Déficit Estrutural:** O saldo negativo por posse aponta para problemas graves na sustentação de vantagens ou na geração de paradas defensivas.")

    for estilo in estilos:
        st.info(estilo, icon="📊")

st.divider()

if not df_elenco.empty:
    st.subheader("⭐ Papéis e Destaques do Elenco")
    df_rotacao = df_elenco[df_elenco['jogos_disputados'] > (df_elenco['jogos_disputados'].max() * 0.3)]
    
    if not df_rotacao.empty:
        c1, c2, c3 = st.columns(3)
        
        motor = df_rotacao.loc[df_rotacao['PPG'].idxmax()]
        c1.markdown(f"### 👑 Motor Ofensivo\n**{motor['nome_completo']}**")
        c1.markdown(f"Principal volume da equipa. Assume a carga pesada do ataque com **{motor['PPG']:.1f} PTS** e um Usage de **{motor['usg_pct']*100:.1f}%**.")
        
        playmaker = df_rotacao.loc[df_rotacao['APG'].idxmax()]
        c2.markdown(f"### 🧠 Facilitador\n**{playmaker['nome_completo']}**")
        c2.markdown(f"Gera a fluidez do ataque. Lidera a equipa na distribuição com **{playmaker['APG']:.1f} AST** por jogo.")
        
        eficiente = df_rotacao.loc[df_rotacao['ts_pct'].idxmax()]
        c3.markdown(f"### 🎯 Eficiência\n**{eficiente['nome_completo']}**")
        c3.markdown(f"Máximo aproveitamento por arremesso. Converte oportunidades com True Shooting de **{eficiente['ts_pct']*100:.1f}%**.")

st.subheader("👥 Depth Chart (A Rotação Completa)")

if not df_elenco.empty:
    titulares = df_elenco.head(5)
    
    # 👇 O PROBLEMA ESTAVA AQUI: Mudámos de .iloc[5:15] para .iloc[5:] para apanhar TODOS os reservas!
    banco = df_elenco.iloc[5:] 
    
    st.markdown("#### 🌟 Core 5 (Prováveis Titulares)")
    cols_tit = st.columns(5)
    for i, row in titulares.iterrows():
        with cols_tit[i]:
            pos = row.get("posicao", "-")
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                <img src="https://cdn.nba.com/headshots/nba/latest/1040x760/{row['jogador_id']}.png" width="100%" style="border-radius: 8px; margin-bottom: 10px; background: radial-gradient(circle, rgba(29,66,138,0.3) 0%, rgba(0,0,0,0) 80%);" />
                <span style="background: #1D428A; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; letter-spacing: 1px;">{pos}</span>
                <h5 style="margin: 10px 0 5px 0; color: #FAFAFA; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['nome_completo']}</h5>
                <div style="color: #FFD700; font-size: 1rem; font-weight: bold;">{row['PPG']:.1f} PTS &nbsp;|&nbsp; {row.get('MPG', 0.0):.1f} MIN</div>
                <div style="color: #aaa; font-size: 0.75rem;">{row['RPG']:.1f} REB &nbsp;|&nbsp; {row['APG']:.1f} AST</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("#### 🪑 Unidade de Rotação e Reservas")
    banco_list = [row for _, row in banco.iterrows()]
    
    # O código já era inteligente o suficiente para montar colunas de 5 indefinidamente
    for i in range(0, len(banco_list), 5):
        cols_banco = st.columns(5)
        for j in range(5):
            if i + j < len(banco_list):
                row = banco_list[i+j]
                pos = row.get("posicao", "-")
                with cols_banco[j]:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 15px; opacity: 0.9;">
                        <img src="https://cdn.nba.com/headshots/nba/latest/1040x760/{row['jogador_id']}.png" width="100%" style="border-radius: 8px; margin-bottom: 10px;" />
                        <span style="background: #444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold;">{pos}</span>
                        <h5 style="margin: 8px 0 4px 0; color: #FAFAFA; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['nome_completo']}</h5>
                        <div style="color: #ccc; font-size: 0.85rem; font-weight: bold;">{row['PPG']:.1f} PTS &nbsp;|&nbsp; {row.get('MPG', 0.0):.1f} MIN</div>
                    </div>
                    """, unsafe_allow_html=True)

    with st.expander("📊 Ver Tabela Completa de Estatísticas Avançadas"):
        df_vis = df_elenco[['nome_completo', 'jogos_disputados', 'MPG', 'PPG', 'RPG', 'APG', 'ts_pct', 'usg_pct', 'net_rating']].copy()
        df_vis['ts_pct'] = df_vis['ts_pct'] * 100
        df_vis['usg_pct'] = df_vis['usg_pct'] * 100
        
        st.dataframe(
            df_vis,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nome_completo": st.column_config.TextColumn("Jogador", width="medium"),
                "jogos_disputados": st.column_config.NumberColumn("GP"),
                "MPG": st.column_config.NumberColumn("MIN", format="%.1f"),
                "PPG": st.column_config.NumberColumn("PTS", format="%.1f"),
                "RPG": st.column_config.NumberColumn("REB", format="%.1f"),
                "APG": st.column_config.NumberColumn("AST", format="%.1f"),
                "ts_pct": st.column_config.ProgressColumn("TS %", format="%.1f%%", min_value=0, max_value=75),
                "usg_pct": st.column_config.ProgressColumn("USG %", format="%.1f%%", min_value=0, max_value=40),
                "net_rating": st.column_config.NumberColumn("Net Rtg", format="%.1f")
            }
        )
else:
    st.warning("Rotação não encontrada para esta franquia.")