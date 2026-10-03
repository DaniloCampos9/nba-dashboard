import streamlit as st
import pandas as pd
from datetime import datetime
from nba_api.stats.static import teams

from data.queries import (
    obter_perfil_jogador, obter_estatisticas_resumo, obter_dados_liga_avancados, 
    obter_dados_completos_liga, obter_estatisticas_defesa, obter_timeline_carreira
)
from utils.calculations import calcular_percentil, gerar_texto_snapshot, gerar_tabela_comparativa
from components.charts import grafico_percentis_snapshot
from utils.archetypes import classificar_arquetipo
from utils.news import obter_noticias_jogador
from utils.logos import obter_url_logo_time
from utils.position_analyzer import analisar_perfil_posicional # 👇 Importando nossa inteligência de posições!

jogador_nome = st.session_state.get('filtro_jogador')

if not jogador_nome or jogador_nome == "Selecione um jogador...":
    st.warning("👈 Por favor, selecione um jogador na barra lateral para começar.")
    st.stop()

perfil = obter_perfil_jogador(jogador_nome)

if perfil:
    jogador_id = perfil.get("id", "")
    url_foto = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{jogador_id}.png"
    
    temporada_selecionada = st.session_state.get('filtro_temporada')
    tipo_temporada = st.session_state.get('filtro_tipo_temporada', 'Regular Season')
    
    stats = obter_estatisticas_resumo(jogador_id, temporada_selecionada, tipo_temporada)
    def_stats = obter_estatisticas_defesa(jogador_id, temporada_selecionada, tipo_temporada)
    arquetipo = classificar_arquetipo(stats, def_stats)
    perfil_tatico = analisar_perfil_posicional(perfil, stats) # 🧠 Analisando papel posicional
    
    # ==========================================
    # CABEÇALHO PREMIUM & ARQUÉTIPO
    # ==========================================
    col_foto, col_info = st.columns([1.5, 4])
    
    with col_foto:
        st.image(url_foto, width=220)
        
    with col_info:
        st.title(perfil.get("nome_completo", jogador_nome))
        
        # Badge de Arquétipo (2K Style)
        if arquetipo:
            badge_html = f"""
            <div style="background: {arquetipo['cor']}; padding: 12px 20px; border-radius: 10px; color: white; display: inline-block; margin-bottom: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <h3 style="margin: 0; font-size: 1.3rem; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                    {arquetipo['icone']} {arquetipo['nome']}
                </h3>
                <p style="margin: 5px 0 0 0; font-size: 0.95rem; opacity: 0.95; line-height: 1.3;">
                    {arquetipo['desc']}
                </p>
            </div>
            """
            st.markdown(badge_html, unsafe_allow_html=True)
        
        # ==========================================
        # 🏀 BANNER DE FRANQUIA ATUAL EM DESTAQUE
        # ==========================================
        time_id_bruto = perfil.get("time_atual_id") or perfil.get("time_id") or perfil.get("team_id")
        nome_do_time = "N/A"
        logo_time_atual = obter_url_logo_time(time_id_bruto)
        
        if time_id_bruto and str(time_id_bruto).isdigit():
            try:
                time_info = teams.find_team_name_by_id(int(time_id_bruto))
                if time_info: nome_do_time = time_info['full_name'] 
            except Exception: nome_do_time = str(time_id_bruto) 
        elif time_id_bruto:
            nome_do_time = str(time_id_bruto)

        logo_tag = f'<img src="{logo_time_atual}" width="42" style="margin-right: 15px; vertical-align: middle;" />' if logo_time_atual else ''
        
        banner_time_html = f"""
        <div style="background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)); border-left: 5px solid #FF4B4B; border: 1px solid rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 10px; margin-bottom: 15px; display: flex; align-items: center;">
            {logo_tag}
            <div>
                <span style="font-size: 0.75rem; color: #aaa; text-transform: uppercase; letter-spacing: 1.5px; font-weight: bold;">Franquia Atual</span>
                <h4 style="margin: 0; color: #FAFAFA; font-size: 1.25rem;">{nome_do_time}</h4>
            </div>
        </div>
        """
        st.markdown(banner_time_html, unsafe_allow_html=True)

        posicao = perfil.get("posicao", "N/A")
        camisa = perfil.get("camisa", "N/A")
        pais = perfil.get("pais", "N/A")
        altura = perfil.get("altura_pes", "N/A")
        peso = perfil.get("peso_lbs", "N/A")
        ano_draft = perfil.get("ano_draft", "N/A")
        
        data_nasc_str = perfil.get("data_nascimento", "")
        idade = "N/A"
        if data_nasc_str:
            try:
                nascimento = datetime.strptime(data_nasc_str[:10], "%Y-%m-%d")
                hoje = datetime.now()
                idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
            except: pass
        
        st.markdown(f"**Camisa:** #{camisa} &nbsp;&nbsp;|&nbsp;&nbsp; **Posição Base:** {posicao} &nbsp;&nbsp;|&nbsp;&nbsp; **Idade:** {idade} anos")
        st.markdown(f"**Físico:** {altura} ft, {peso} lbs &nbsp;&nbsp;|&nbsp;&nbsp; **Draft:** {ano_draft} &nbsp;&nbsp;|&nbsp;&nbsp; **País:** {pais}")
        st.caption(f"Analisando dados da temporada **{temporada_selecionada}** ({tipo_temporada})")
        
    st.divider()

    # ==========================================
    # 🧬 PERFIL TÁTICO & VERSATILIDADE POSICIONAL
    # ==========================================
    with st.expander("🧬 Análise de Papel Tático e Versatilidade Posicional", expanded=True):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"**Papel em Quadra (Role):** `{perfil_tatico['papel']}`")
            st.markdown(f"**Posição Ideal no Sistema:** `{perfil_tatico.get('posicao_ideal', 'N/A')}`")
        with col_t2:
            st.markdown(f"**Grau de Versatilidade:** `{perfil_tatico['versatilidade']}`")
        
        st.markdown(f"**Impacto Dominante:** {perfil_tatico.get('dominancia', '')}")
    
    st.divider()
    
    # ==========================================
    # SEÇÃO DE ESTATÍSTICAS E KPIS
    # ==========================================
    st.subheader("📊 Player Snapshot & KPIs")
    
    if stats:
        jogos = stats.get("jogos_disputados", 0)
        if jogos > 0:
            ppg = round(stats.get("pontos_totais", 0) / jogos, 1)
            rpg = round(stats.get("rebotes_totais", 0) / jogos, 1)
            apg = round(stats.get("assistencias_totais", 0) / jogos, 1)
        else: ppg = rpg = apg = "N/A"
            
        ts_pct_raw = stats.get("ts_pct")
        ts_pct = f"{round(ts_pct_raw * 100, 1)}%" if pd.notnull(ts_pct_raw) else "N/A"
        
        usg_pct_raw = stats.get("usg_pct")
        usg_pct = f"{round(usg_pct_raw * 100, 1)}%" if pd.notnull(usg_pct_raw) else "N/A"
        
        net_rating = stats.get("net_rating", "N/A")
        if isinstance(net_rating, float): net_rating = round(net_rating, 1)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PPG", ppg, help="Points Per Game (Pontos por jogo)")
            st.metric("USG%", usg_pct, help="Usage Rate: Volume de posses finalizadas por este jogador.")
            
        with col2:
            st.metric("RPG", rpg, help="Rebounds Per Game (Rebotes por jogo)")
            st.metric("TS%", ts_pct, help="True Shooting: Eficiência total considerando lances livres e 3pt.")
            
        with col3:
            st.metric("APG", apg, help="Assists Per Game (Assistências por jogo)")
            st.metric("Net Rating", net_rating, help="Saldo de pontos da equipe a cada 100 posses de bola.")
            
        with col4:
            pie_raw = stats.get("pie")
            pie = f"{round(pie_raw * 100, 1)}%" if pd.notnull(pie_raw) else "N/A"
            ast_pct_raw = stats.get("ast_pct")
            ast_pct = f"{round(ast_pct_raw * 100, 1)}%" if pd.notnull(ast_pct_raw) else "N/A"
            
            st.metric("PIE", pie, help="Mede a % de eventos positivos do jogo criados pelo jogador.")
            st.metric("AST%", ast_pct, help="Estimativa da % de cestas assistidas por ele.")
        
        st.divider()
        
        # ==========================================
        # CONFRONTO CONTRA A LIGA
        # ==========================================
        st.markdown("### ⚖️ Player vs League Landscape")
        
        dados_liga = obter_dados_liga_avancados(temporada_selecionada, tipo_temporada)
        df_liga_completo = obter_dados_completos_liga(temporada_selecionada, tipo_temporada)
        
        lista_usg_liga = [jog.get("usg_pct") for jog in dados_liga if jog.get("usg_pct") is not None]
        lista_ts_liga = [jog.get("ts_pct") for jog in dados_liga if jog.get("ts_pct") is not None]
        
        usg_percentil = calcular_percentil(stats.get("usg_pct"), lista_usg_liga)
        ts_percentil = calcular_percentil(stats.get("ts_pct"), lista_ts_liga)
        texto_resumo = gerar_texto_snapshot(usg_percentil, ts_percentil)
        
        col_grafico, col_tabela = st.columns([1, 1.2])
        
        with col_grafico:
            st.info(f"💡 {texto_resumo}")
            if usg_percentil is not None and ts_percentil is not None:
                fig_percentis = grafico_percentis_snapshot(usg_percentil, ts_percentil)
                st.plotly_chart(fig_percentis, use_container_width=True, config={'displayModeBar': False})
                
        with col_tabela:
            st.markdown("O **Percentil** indica onde o atleta está no ranqueamento da NBA (ex: 90º = melhor que 90% da liga).")
            if not df_liga_completo.empty:
                df_comparativo = gerar_tabela_comparativa(stats, df_liga_completo)
                st.dataframe(df_comparativo, use_container_width=True, hide_index=True)
            else:
                st.warning("Não foi possível carregar as médias da liga.")
                
        st.divider()

        # ==========================================
        # 📰 FEED DE NOTÍCIAS EM TEMPO REAL
        # ==========================================
        st.markdown(f"### 📰 Latest News & Rumors: {jogador_nome}")
        st.caption("Últimas atualizações, análises e movimentações coletadas em tempo real da web.")
        
        noticias = obter_noticias_jogador(jogador_nome)
        
        if noticias:
            cols_news = st.columns(len(noticias) if len(noticias) <= 4 else 4)
            for i, noticia in enumerate(noticias[:4]):
                with cols_news[i]:
                    with st.container(border=True):
                        st.markdown(f"**{noticia['titulo']}**")
                        st.caption(f"📅 {noticia['data']}")
                        st.markdown(f"[Ler matéria]({noticia['link']})")
        else:
            st.info("Nenhuma notícia recente encontrada no momento para este atleta.")

        st.divider()

        # ==========================================
        # ⏳ TIMELINE DE CARREIRA & FRANQUIAS (EXPANSÍVEL)
        # ==========================================
        with st.expander("⏳ Ver Histórico Completo de Carreira (Franquias e Temporadas Anteriores)", expanded=False):
            with st.spinner("Carregando linha do tempo da carreira..."):
                df_reg, df_play = obter_timeline_carreira(jogador_id)
            
            if not df_reg.empty:
                df_times_unicos = df_reg[df_reg['TEAM_ABBREVIATION'] != 'TOT'].copy()
                times_passados = df_times_unicos['TEAM_ABBREVIATION'].unique()
                
                st.markdown("**Franquias Representadas na Carreira:**")
                cols_teams = st.columns(len(times_passados) if len(times_passados) <= 6 else 6)
                
                for idx, time_abrev in enumerate(times_passados):
                    col_idx = idx % 6
                    logo_url_franquia = obter_url_logo_time(time_abrev)
                    logo_html = f'<img src="{logo_url_franquia}" width="38" style="margin-bottom: 6px;"/>' if logo_url_franquia else ''
                    
                    with cols_teams[col_idx]:
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                            {logo_html}
                            <h4 style="margin: 0; color: #FAFAFA; font-size: 0.85rem;">{time_abrev}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("##### 📈 Temporada Regular (Carreira Inteira)")
                df_exibicao = df_reg[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB']].copy()
                df_exibicao['PPG'] = (df_exibicao['PTS'] / df_exibicao['GP']).round(1)
                df_exibicao['APG'] = (df_exibicao['AST'] / df_exibicao['GP']).round(1)
                df_exibicao['RPG'] = (df_exibicao['REB'] / df_exibicao['GP']).round(1)
                df_exibicao = df_exibicao[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PPG', 'RPG', 'APG']]
                df_exibicao.columns = ['Temporada', 'Time', 'Jogos', 'PPG', 'RPG', 'APG']
                st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

                if not df_play.empty:
                    st.markdown("##### 💍 Playoffs (Carreira Inteira)")
                    df_play_ex = df_play[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB']].copy()
                    df_play_ex['PPG'] = (df_play_ex['PTS'] / df_play_ex['GP']).round(1)
                    df_play_ex['APG'] = (df_play_ex['AST'] / df_play_ex['GP']).round(1)
                    df_play_ex['RPG'] = (df_play_ex['REB'] / df_play_ex['GP']).round(1)
                    df_play_ex = df_play_ex[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PPG', 'RPG', 'APG']]
                    df_play_ex.columns = ['Temporada', 'Time', 'Jogos', 'PPG', 'RPG', 'APG']
                    st.dataframe(df_play_ex, use_container_width=True, hide_index=True)
            else:
                st.warning("Histórico de carreira indisponível.")