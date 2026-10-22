import streamlit as st
import pandas as pd
from components.navigation import renderizar_menu_superior
from data.queries import obter_hot_streaks_supabase

renderizar_menu_superior()

TEMPORADA_ATUAL = "2026-27"

st.title(f"🔥 Radar de Momento — Hot Streaks ({TEMPORADA_ATUAL})")
st.caption("Recorte dinâmico dos **Últimos 5 Jogos** de cada equipe direto do banco de dados, sem trava de jogos mínimos.")

with st.spinner("Carregando termômetro da liga..."):
    df_mom, df_clutch = obter_hot_streaks_supabase(TEMPORADA_ATUAL)

if df_mom.empty:
    st.warning("Ainda não há dados de momento salvos para 2026-27. Rode o `python main.py` para alimentar a tabela `stats_momento`.")
    st.stop()

# ==========================================
# DESTAQUES DO MOMENTO (HERO CARDS)
# ==========================================
st.subheader("⚡ Os Caras do Momento (Últimos 5 Jogos)")
c1, c2, c3, c4 = st.columns(4)

top_scorer = df_mom.sort_values(by=["PPG", "TS%"], ascending=[False, False]).iloc[0]
top_delta = df_mom.sort_values(by=["DELTA_PPG", "PPG"], ascending=[False, False]).iloc[0]
top_def = df_mom.sort_values(by=["STOCKS", "BPG"], ascending=[False, False]).iloc[0]
top_pie = df_mom.sort_values(by=["PIE%", "net_rating"], ascending=[False, False]).iloc[0]

def render_card_destaque(col, titulo, icone, row, metrica_principal, sub_metrica, cor_borda):
    with col:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.04); border-top: 4px solid {cor_borda}; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.25);">
            <div style="font-size: 0.8rem; color: #aaa; font-weight: bold; margin-bottom: 6px;">{icone} {titulo}</div>
            <img src="https://cdn.nba.com/headshots/nba/latest/1040x760/{row['jogador_id']}.png" width="110" style="border-radius: 50%; background: rgba(255,255,255,0.05); margin-bottom: 8px;" />
            <h4 style="margin: 4px 0 2px 0; font-size: 1.05rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{row['nome_completo']}</h4>
            <span style="background: #222; color: #ccc; padding: 2px 8px; border-radius: 8px; font-size: 0.75rem;">{row['time_abrev']} • {int(row['gp'])} J</span>
            <div style="color: {cor_borda}; font-size: 1.3rem; font-weight: 800; margin-top: 8px;">{metrica_principal}</div>
            <div style="color: #888; font-size: 0.8rem;">{sub_metrica}</div>
        </div>
        """, unsafe_allow_html=True)

render_card_destaque(c1, "Cestinha do Momento", "🎯", top_scorer, f"{top_scorer['PPG']:.1f} PPG", f"TS%: {top_scorer['TS%']:.1f}% | 3PM: {top_scorer['3PM']:.1f}", "#FF4B4B")
render_card_destaque(c2, "Maior Salto (Esquentou)", "📈", top_delta, f"+{top_delta['DELTA_PPG']:.1f} PPG", f"Recente: {top_delta['PPG']:.1f} vs Temp: {top_delta['PPG_SEASON']:.1f}", "#FFA500")
render_card_destaque(c3, "Xerife Defensivo", "🛡️", top_def, f"{top_def['STOCKS']:.1f} Stocks", f"{top_def['SPG']:.1f} STL + {top_def['BPG']:.1f} BLK", "#00C9FF")
render_card_destaque(c4, "Dominância Global", "👑", top_pie, f"{top_pie['PIE%']:.1f}% PIE", f"Net Rtg: {top_pie['net_rating']:+.1f}", "#FFD700")

st.divider()

# ==========================================
# TABELAS DETALHADAS POR CATEGORIA
# ==========================================
config_colunas = {
    "nome_completo": st.column_config.TextColumn("Atleta", width="medium"),
    "time_abrev": st.column_config.TextColumn("Time", width="small"),
    "gp": st.column_config.NumberColumn("Jogos (Janela)"),
    "MPG": st.column_config.NumberColumn("MIN", format="%.1f"),
    "PPG": st.column_config.NumberColumn("PTS/J", format="%.1f"),
    "DELTA_PPG": st.column_config.NumberColumn("Delta vs Temp.", format="%+.1f"),
    "RPG": st.column_config.NumberColumn("REB/J", format="%.1f"),
    "APG": st.column_config.NumberColumn("AST/J", format="%.1f"),
    "3PM": st.column_config.NumberColumn("3PM/J", format="%.1f"),
    "3P%": st.column_config.NumberColumn("3P%", format="%.1f%%"),
    "TS%": st.column_config.ProgressColumn("Eficiência (TS%)", format="%.1f%%", min_value=35, max_value=80),
    "USG%": st.column_config.ProgressColumn("Volume (USG%)", format="%.1f%%", min_value=10, max_value=45),
    "SPG": st.column_config.NumberColumn("Roubos/J", format="%.1f"),
    "BPG": st.column_config.NumberColumn("Tocos/J", format="%.1f"),
    "STOCKS": st.column_config.NumberColumn("Stocks (STL+BLK)", format="%.1f"),
    "net_rating": st.column_config.NumberColumn("Net Rtg", format="%+.1f"),
    "PLUS_MINUS_PG": st.column_config.NumberColumn("+/- por Jogo", format="%+.1f"),
    "PIE%": st.column_config.ProgressColumn("Impacto (PIE)", format="%.1f%%", min_value=0, max_value=30)
}

aba_ataque, aba_defesa, aba_impacto, aba_clutch = st.tabs([
    "🎯 Explosão Ofensiva", 
    "🛡️ Muralhas Defensivas", 
    "⚡ Impacto & Plus/Minus",
    "🧊 Sangue Frio (Clutch)"
])

with aba_ataque:
    st.markdown("##### 🔥 Líderes de Pontuação e Evolução Recente")
    df_atq = df_mom.sort_values(by=["PPG", "TS%"], ascending=[False, False]).head(25)
    st.dataframe(
        df_atq[['nome_completo', 'time_abrev', 'gp', 'MPG', 'PPG', 'DELTA_PPG', '3PM', '3P%', 'TS%', 'USG%']],
        column_config=config_colunas, hide_index=True, use_container_width=True
    )

with aba_defesa:
    st.markdown("##### 🔒 Líderes em Disruptividade (Roubos + Tocos nos últimos 5 jogos)")
    df_def = df_mom.sort_values(by=["STOCKS", "SPG", "BPG"], ascending=[False, False, False]).head(25)
    st.dataframe(
        df_def[['nome_completo', 'time_abrev', 'gp', 'MPG', 'STOCKS', 'SPG', 'BPG', 'RPG', 'net_rating']],
        column_config=config_colunas, hide_index=True, use_container_width=True
    )

with aba_impacto:
    st.markdown("##### ⚡ Dominância Geral (PIE, Assistências e Saldo de Pontos)")
    df_imp = df_mom.sort_values(by=["PIE%", "PLUS_MINUS_PG"], ascending=[False, False]).head(25)
    st.dataframe(
        df_imp[['nome_completo', 'time_abrev', 'gp', 'MPG', 'PIE%', 'PPG', 'RPG', 'APG', 'PLUS_MINUS_PG', 'net_rating']],
        column_config=config_colunas, hide_index=True, use_container_width=True
    )

with aba_clutch:
    st.markdown("##### 🧊 Decisivos no Final de Jogo (Últimos 5 min com placar até 5 pts na temporada 2026-27)")
    if not df_clutch.empty:
        df_cl = df_clutch.sort_values(by="clutch_pts", ascending=False).head(25)
        st.dataframe(
            df_cl[['nome_completo', 'clutch_pts', 'CLUTCH_FG%', 'CLUTCH_3P%', 'CLUTCH_USG%', 'clutch_net_rating']],
            column_config={
                "nome_completo": st.column_config.TextColumn("Atleta", width="medium"),
                "clutch_pts": st.column_config.NumberColumn("Pontos Clutch", format="%.1f"),
                "CLUTCH_FG%": st.column_config.ProgressColumn("FG% Clutch", format="%.1f%%", min_value=0, max_value=100),
                "CLUTCH_3P%": st.column_config.NumberColumn("3P% Clutch", format="%.1f%%"),
                "CLUTCH_USG%": st.column_config.ProgressColumn("USG% Clutch", format="%.1f%%", min_value=0, max_value=50),
                "clutch_net_rating": st.column_config.NumberColumn("Saldo/Net Clutch", format="%+.1f")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("Ainda não há registros de Clutch Time salvos para 2026-27.")