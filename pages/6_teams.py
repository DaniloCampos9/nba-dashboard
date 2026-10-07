import streamlit as st
import pandas as pd
from data.queries import obter_identidade_time, obter_elenco_time, obter_momento_recente

# Recupera os filtros globais
temporada = st.session_state.get('filtro_temporada', '2026-27')
tipo_temporada = st.session_state.get('filtro_tipo_temporada', 'Regular Season')
time_selecionado = st.session_state.get('filtro_time', 'Selecione um time...')

if time_selecionado == "Selecione um time...":
    st.warning("👈 Selecione uma franquia na barra lateral para visualizar o Relatório de Scouting.")
    st.stop()

st.title(f"🏀 {time_selecionado} | Scouting Report")
st.markdown(f"**Temporada:** {temporada} | **Fase:** {tipo_temporada}")
st.divider()

dados_time = obter_identidade_time(time_selecionado, temporada, tipo_temporada)
df_elenco = obter_elenco_time(time_selecionado, temporada, tipo_temporada)

if dados_time:
    # 1. OVERVIEW & FOUR FACTORS (Visão Analítica)
    st.subheader("Eficiência e Ritmo")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Offensive Rating", f"{dados_time.get('off_rating', 0):.1f}", help="Pontos anotados por 100 posses")
    col2.metric("Defensive Rating", f"{dados_time.get('def_rating', 0):.1f}", help="Pontos sofridos por 100 posses", delta_color="inverse")
    col3.metric("Net Rating", f"{dados_time.get('net_rating', 0):.1f}", help="Saldo de pontos por 100 posses")
    col4.metric("Pace", f"{dados_time.get('pace', 0):.1f}", help="Número de posses de bola por 48 minutos")

    # 2. IDENTIDADE DA EQUIPE (Análise Textual Dinâmica)
    st.markdown("### 🧬 Perfil e Estilo de Jogo")
    
    estilos = []
    pace = dados_time.get('pace', 0)
    
    # Exemplo de lógica baseada no Pace (Podemos expandir se você tiver % de 3 pts e AST% no banco)
    if pace > 100.5:
        estilos.append("**Pace & Space / Transição Rápida:** A equipe atua em um dos ritmos mais acelerados da liga, buscando definir as jogadas rapidamente antes da defesa adversária se estabelecer.")
    elif pace < 98 and pace > 0:
        estilos.append("**Meia-Quadra Metódico:** A equipe opera em ritmo cadenciado, priorizando a execução tática de meia-quadra e reduzindo o número total de posses no jogo.")
    
    net_rtg = dados_time.get('net_rating', 0)
    if net_rtg > 4.5:
        estilos.append("**Dominância Sustentável:** O Net Rating indica um perfil de *Contender* real, vencendo seus minutos de forma contundente e consistente.")
    elif net_rtg < -4:
        estilos.append("**Déficit Estrutural:** O saldo negativo por posse aponta para problemas graves na sustentação de vantagens ou na geração de paradas defensivas.")

    for estilo in estilos:
        st.info(estilo, icon="📊")

st.divider()

# 3. QUEM É QUEM (Os Motores da Franquia & Recorte de Momento)
if not df_elenco.empty:
    st.subheader("⭐ Papéis e Destaques do Elenco")
    
    df_rotacao = df_elenco[df_elenco['jogos_disputados'] > (df_elenco['jogos_disputados'].max() * 0.3)]
    
    if not df_rotacao.empty:
        # Agora usamos 4 colunas para caber o "Momento Recente"
        c1, c2, c3, c4 = st.columns(4)
        
        motor = df_rotacao.loc[df_rotacao['PPG'].idxmax()]
        c1.markdown(f"### 👑 Motor Ofensivo\n**{motor['nome_completo']}**")
        c1.markdown(f"Principal volume do time. Assume a carga pesada do ataque com **{motor['PPG']:.1f} PTS** e um Usage de **{motor['usg_pct']*100:.1f}%**.")
        
        playmaker = df_rotacao.loc[df_rotacao['APG'].idxmax()]
        c2.markdown(f"### 🧠 Facilitador\n**{playmaker['nome_completo']}**")
        c2.markdown(f"Gera a fluidez do ataque. Lidera a equipe na distribuição com **{playmaker['APG']:.1f} AST** por jogo.")
        
        eficiente = df_rotacao.loc[df_rotacao['ts_pct'].idxmax()]
        c3.markdown(f"### 🎯 Eficiência\n**{eficiente['nome_completo']}**")
        c3.markdown(f"Máximo aproveitamento por arremesso. Converte oportunidades com True Shooting de **{eficiente['ts_pct']*100:.1f}%**.")

        # --- O NOVO RECORTE DE MOMENTO ---
        destaque_recente = obter_momento_recente(time_selecionado, temporada)
        if destaque_recente:
            c4.markdown(f"### 🔥 Em Alta (L10)\n**{destaque_recente['nome']}**")
            c4.markdown(f"Destaque absoluto nos últimos 10 jogos. Média de **{destaque_recente['ppg']} PTS** com **{destaque_recente['fg_pct']}%** nos arremessos.")
        else:
            c4.markdown(f"### 🔥 Em Alta (L10)\n*Dados em processamento*")
            c4.markdown("O recorte de momento exige uma amostra válida de jogos recentes nesta temporada.")
# 4. ROTAÇÃO DETALHADA
st.subheader("👥 Profundidade do Elenco")
if not df_elenco.empty:
    df_vis = df_elenco[['nome_completo', 'jogos_disputados', 'PPG', 'RPG', 'APG', 'ts_pct', 'usg_pct', 'net_rating']].copy()
    df_vis['ts_pct'] = df_vis['ts_pct'] * 100
    df_vis['usg_pct'] = df_vis['usg_pct'] * 100
    
    st.dataframe(
        df_vis,
        use_container_width=True,
        hide_index=True,
        column_config={
            "nome_completo": st.column_config.TextColumn("Jogador", width="medium"),
            "jogos_disputados": st.column_config.NumberColumn("GP", help="Jogos Disputados"),
            "PPG": st.column_config.NumberColumn("PTS", format="%.1f"),
            "RPG": st.column_config.NumberColumn("REB", format="%.1f"),
            "APG": st.column_config.NumberColumn("AST", format="%.1f"),
            "ts_pct": st.column_config.ProgressColumn("TS %", help="Eficiência real de arremesso", format="%.1f%%", min_value=0, max_value=75),
            "usg_pct": st.column_config.ProgressColumn("USG %", help="Volume de uso no ataque", format="%.1f%%", min_value=0, max_value=40),
            "net_rating": st.column_config.NumberColumn("Net Rtg", help="Impacto em quadra por 100 posses", format="%.1f")
        }
    )
else:
    st.warning("Rotação não encontrada para esta franquia.")