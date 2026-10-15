import streamlit as st
import pandas as pd
from datetime import datetime
from nba_api.stats.static import teams

from components.navigation import renderizar_menu_superior, cascata_jogadores
from data.queries import (
    obter_perfil_jogador, obter_estatisticas_resumo, obter_dados_liga_avancados, 
    obter_dados_completos_liga, obter_estatisticas_defesa, obter_timeline_carreira,
    obter_benchmarking_jogador
)
from utils.calculations import calcular_percentil, gerar_texto_snapshot, gerar_tabela_comparativa
from components.charts import grafico_percentis_snapshot
from utils.archetypes import classificar_arquetipo
from utils.news import obter_noticias_jogador
from utils.logos import obter_url_logo_time
from utils.position_analyzer import analisar_perfil_posicional 
from utils.narrative_engine import gerar_scouting_report_dinamico

renderizar_menu_superior()
jogador_nome, temporada_selecionada, tipo_temporada = cascata_jogadores()
modo_visao = st.session_state.get('modo_visao', 'Por Temporada')
perfil = obter_perfil_jogador(jogador_nome)

if perfil:
    jogador_id = perfil.get("id", "")
    url_foto = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{jogador_id}.png"
    
    if modo_visao == "Carreira (All-Time)":
        df_reg_carreira, _ = obter_timeline_carreira(jogador_id)
        if not df_reg_carreira.empty:
            total_jogos = df_reg_carreira['gp'].sum()
            stats = {
                'jogos_disputados': int(total_jogos),
                'pontos_totais': int(df_reg_carreira['pts'].sum()),
                'rebotes_totais': int(df_reg_carreira['reb'].sum()),
                'assistencias_totais': int(df_reg_carreira['ast'].sum()),
            }
        else: stats = {}
        def_stats = {}
        arquetipo = None
        perfil_tatico = {"papel": "Lenda / Jogador Histórico", "versatilidade": "Consolidado na Carreira"}
    else:
        stats = obter_estatisticas_resumo(jogador_id, temporada_selecionada, tipo_temporada)
        if not stats:
            st.warning(f"Não há dados suficientes ou o jogador não atuou na temporada {temporada_selecionada} ({tipo_temporada}).")
            st.stop()
        def_stats = obter_estatisticas_defesa(jogador_id, temporada_selecionada, tipo_temporada)
        arquetipo = classificar_arquetipo(stats, def_stats)
        perfil_tatico = analisar_perfil_posicional(perfil, stats)
        
    col_foto, col_info = st.columns([1.5, 4])
    with col_foto:
        st.image(url_foto, width=220)
        
    with col_info:
        st.title(perfil.get("nome_completo", jogador_nome))
        
        if arquetipo and modo_visao != "Carreira (All-Time)":
            badge_html = f"""
            <div style="background: {arquetipo['cor']}; padding: 12px 20px; border-radius: 10px; color: white; display: inline-block; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size: 1.3rem; color: white;">{arquetipo['icone']} {arquetipo['nome']}</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.95rem;">{arquetipo['desc']}</p>
            </div>
            """
            st.markdown(badge_html, unsafe_allow_html=True)
        
        time_id_bruto = perfil.get("time_atual_id") or perfil.get("time_id") or perfil.get("team_id")
        nome_do_time = "N/A"
        logo_time_atual = obter_url_logo_time(time_id_bruto)
        
        if time_id_bruto and str(time_id_bruto).isdigit():
            try:
                time_info = teams.find_team_name_by_id(int(time_id_bruto))
                if time_info: nome_do_time = time_info['full_name'] 
            except: nome_do_time = str(time_id_bruto) 
        elif time_id_bruto: nome_do_time = str(time_id_bruto)

        logo_tag = f'<img src="{logo_time_atual}" width="42" style="margin-right: 15px; vertical-align: middle;" />' if logo_time_atual else ''
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); border-left: 5px solid #FF4B4B; padding: 12px 20px; border-radius: 10px; margin-bottom: 15px; display: flex; align-items: center;">
            {logo_tag}<div><span style="font-size: 0.75rem; color: #aaa;">Franquia Atual</span>
            <h4 style="margin: 0; color: #FAFAFA;">{nome_do_time}</h4></div>
        </div>
        """, unsafe_allow_html=True)

        posicao = perfil.get("posicao", "N/A")
        camisa = perfil.get("camisa", "N/A")
        pais = perfil.get("pais", "N/A")
        altura = perfil.get("altura_pes", "N/A")
        peso = perfil.get("peso_lbs", "N/A")
        
        data_nasc_str = perfil.get("data_nascimento", "")
        idade = "N/A"
        if data_nasc_str:
            try:
                nascimento = datetime.strptime(data_nasc_str[:10], "%Y-%m-%d")
                idade = datetime.now().year - nascimento.year
            except: pass
        
        st.markdown(f"**Camisa:** #{camisa} | **Posição Base:** {posicao} | **Idade:** {idade} anos")
        st.markdown(f"**Físico:** {altura} ft, {peso} lbs | **País:** {pais}")
        
        with st.container(border=True):
            st.markdown("#### 🕵️‍♂️ AI Scouting Report")
            if modo_visao == "Carreira (All-Time)":
                st.info("Alterne para o modo 'Por Temporada' na etapa 2 para visualizar o relatório tático dinâmico de inteligência artificial.")
            else:
                relatorio = gerar_scouting_report_dinamico(nome=perfil.get("nome_completo", jogador_nome), stats=stats, def_stats=def_stats, perfil_tatico=perfil_tatico)
                st.info(relatorio)
    
    st.divider()

    if modo_visao != "Carreira (All-Time)":
        with st.expander("🧬 Análise de Papel Tático e Versatilidade Posicional", expanded=True):
            c_t1, c_t2 = st.columns(2)
            c_t1.markdown(f"**Papel em Quadra (Role):** `{perfil_tatico['papel']}`\n**Posição Ideal no Sistema:** `{perfil_tatico.get('posicao_ideal', 'N/A')}`")
            c_t2.markdown(f"**Grau de Versatilidade:** `{perfil_tatico['versatilidade']}`")
            st.markdown(f"**Impacto Dominante:** {perfil_tatico.get('dominancia', '')}")
        st.divider()
    
    st.subheader("📊 Resumo de Produção (Player Snapshot)")
    
    if modo_visao == "Carreira (All-Time)":
        st.caption("🏆 Exibindo médias brutas acumuladas e conquistas na história da NBA.")
        
        lista_trofeus = [
            ("💍 Títulos", perfil.get("campeonatos", 0)), ("🏆 Finals MVP", perfil.get("fmvp", 0)),
            ("👑 MVP", perfil.get("mvp", 0)), ("🛡️ DPOY", perfil.get("dpoy", 0)),
            ("🌱 ROY", perfil.get("roy", 0)), ("⚡ 6th Man", perfil.get("smoy", 0)),
            ("📈 MIP", perfil.get("mip", 0)), ("⭐ All-Star", perfil.get("all_star", 0)),
            ("🏅 All-NBA", perfil.get("all_nba", 0)), ("🔒 All-Defensive", perfil.get("all_defensive", 0))
        ]
        trofeus_validos = [(n, v) for n, v in lista_trofeus if v > 0]
        
        if trofeus_validos:
            st.markdown("#### 🏆 Sala de Troféus")
            for i in range(0, len(trofeus_validos), 5):
                cols = st.columns(5)
                for j in range(5):
                    if i + j < len(trofeus_validos):
                        cols[j].metric(trofeus_validos[i+j][0], trofeus_validos[i+j][1])
            st.divider()
        
        if stats and stats.get("jogos_disputados", 0) > 0:
            jogos = stats["jogos_disputados"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Jogos na Carreira", jogos)
            c2.metric("Pontos (Carreira)", round(stats.get("pontos_totais", 0) / jogos, 1))
            c3.metric("Rebotes (Carreira)", round(stats.get("rebotes_totais", 0) / jogos, 1))
            c4.metric("Assistências (Carreira)", round(stats.get("assistencias_totais", 0) / jogos, 1))
    else:
        st.caption("📋 **O que é isto?** O Percentil compara o jogador com o resto da liga (ex: 90º significa ser melhor do que 90% dos jogadores na NBA nesta métrica).")
        benchmarks = obter_benchmarking_jogador(jogador_id, temporada_selecionada, tipo_temporada)
        
        if benchmarks and 'PPG' in benchmarks:
            col1, col2, col3, col4 = st.columns(4)
            def render_metric(coluna_st, bm_key):
                if bm_key in benchmarks:
                    bm = benchmarks[bm_key]
                    suf = "%" if bm['is_pct'] else ""
                    coluna_st.metric(bm['nome'], f"{bm['valor']:.1f}{suf}", bm['classificacao'], delta_color=bm['cor'])
                    coluna_st.caption(f"Liga: {bm['media_liga']:.1f}{suf} | Perc: {bm['percentil']:.0f}")

            with col1:
                render_metric(st, 'PPG')
                render_metric(st, 'usg_pct')
            with col2:
                render_metric(st, 'RPG')
                render_metric(st, 'ts_pct')
            with col3:
                render_metric(st, 'APG')
                render_metric(st, 'net_rating')
            with col4:
                render_metric(st, 'pie')
                render_metric(st, 'ast_pct')
        else:
            st.warning("O jogador não atingiu o mínimo de 10 jogos nesta temporada.")

    st.divider()
    
    if modo_visao != "Carreira (All-Time)":
        st.markdown("### 🎯 Eficiência de Perímetro")
        st.caption("📋 **Como ler:** O Volume mostra as tentativas por jogo. Um arremessador de elite possui mais de 37% de aproveitamento em alto volume.")
        jogos_validos = stats.get("jogos_disputados", 1) if stats else 1
        if jogos_validos == 0: jogos_validos = 1
        fg3m, fg3a = stats.get("fg3m_totais", 0) / jogos_validos if stats else 0, stats.get("fg3a_totais", 0) / jogos_validos if stats else 0
        pct_3 = (fg3m / fg3a * 100) if fg3a > 0 else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Aproveitamento (3P%)", f"{pct_3:.1f}%")
        c2.metric("Volume (3PA/jogo)", f"{fg3a:.1f}")
        c3.metric("Conversão (3PM/jogo)", f"{fg3m:.1f}")
        st.divider()
        
        st.markdown("### ⚖️ Player vs League Landscape")
        st.caption("📋 **O que é isto?** O gráfico ilustra visualmente a posição do atleta na hierarquia de volume (uso de posses) e eficiência da NBA atual.")
        dados_liga = obter_dados_liga_avancados(temporada_selecionada, tipo_temporada)
        df_liga_completo = obter_dados_completos_liga(temporada_selecionada, tipo_temporada)
        
        lista_usg_liga = [jog.get("usg_pct") for jog in dados_liga if jog.get("usg_pct") is not None]
        lista_ts_liga = [jog.get("ts_pct") for jog in dados_liga if jog.get("ts_pct") is not None]
        usg_percentil, ts_percentil = calcular_percentil(stats.get("usg_pct"), lista_usg_liga), calcular_percentil(stats.get("ts_pct"), lista_ts_liga)
        
        col_grafico, col_tabela = st.columns([1, 1.2])
        with col_grafico:
            st.info(f"💡 {gerar_texto_snapshot(usg_percentil, ts_percentil)}")
            if usg_percentil is not None and ts_percentil is not None:
                st.plotly_chart(grafico_percentis_snapshot(usg_percentil, ts_percentil), use_container_width=True, config={'displayModeBar': False})
        with col_tabela:
            if not df_liga_completo.empty:
                st.dataframe(gerar_tabela_comparativa(stats, df_liga_completo), use_container_width=True, hide_index=True)

        st.divider()

    st.markdown(f"### 📰 Latest News & Rumors: {jogador_nome}")
    noticias = obter_noticias_jogador(jogador_nome)
    if noticias:
        cols_news = st.columns(len(noticias) if len(noticias) <= 4 else 4)
        for i, noticia in enumerate(noticias[:4]):
            with cols_news[i].container(border=True):
                st.markdown(f"**{noticia['titulo']}**\n\n📅 {noticia['data']}\n\n[Ler matéria]({noticia['link']})")
    st.divider()

    with st.expander("⏳ Ver Histórico Completo de Carreira (Linha do Tempo)", expanded=(modo_visao == "Carreira (All-Time)")):
        df_reg, df_play = obter_timeline_carreira(jogador_id)
        if not df_reg.empty:
            df_reg.columns = df_reg.columns.str.upper()
            st.markdown("##### 📈 Temporada Regular")
            df_exibicao = df_reg[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB']].copy()
            df_exibicao['PPG'], df_exibicao['RPG'], df_exibicao['APG'] = (df_exibicao['PTS'] / df_exibicao['GP']).round(1), (df_exibicao['REB'] / df_exibicao['GP']).round(1), (df_exibicao['AST'] / df_exibicao['GP']).round(1)
            st.dataframe(df_exibicao[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PPG', 'RPG', 'APG']], use_container_width=True, hide_index=True)