import streamlit as st
from datetime import datetime
from nba_api.stats.static import teams

from data.queries import (
    obter_perfil_jogador, 
    obter_estatisticas_resumo, 
    obter_dados_liga_avancados, 
    obter_dados_completos_liga
)
from utils.calculations import calcular_percentil, gerar_texto_snapshot, gerar_tabela_comparativa
from components.charts import grafico_percentis_snapshot


# Puxa o nome do jogador que o usuário escolheu na barra lateral
jogador_nome = st.session_state.get('filtro_jogador')

if not jogador_nome or jogador_nome == "Selecione um jogador...":
    st.warning("👈 Por favor, selecione um jogador na barra lateral para começar.")
    st.stop()

# Busca todas as informações do jogador no banco
perfil = obter_perfil_jogador(jogador_nome)

if perfil:
    # A foto oficial da NBA usa o ID exato que está no seu banco!
    jogador_id = perfil.get("id", "")
    url_foto = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{jogador_id}.png"
    
    # Criando o Layout do Cabeçalho
    col_foto, col_info = st.columns([1, 4])
    
    with col_foto:
        st.image(url_foto, width=180)
        
    with col_info:
        st.title(perfil.get("nome_completo", jogador_nome))
        
        posicao = perfil.get("posicao", "N/A")
        camisa = perfil.get("camisa", "N/A")
        pais = perfil.get("pais", "N/A")
        altura = perfil.get("altura_pes", "N/A")
        peso = perfil.get("peso_lbs", "N/A")
        
        # Calculando a idade a partir da data de nascimento
        data_nasc_str = perfil.get("data_nascimento", "")
        idade = "N/A"
        if data_nasc_str:
            try:
                nascimento = datetime.strptime(data_nasc_str[:10], "%Y-%m-%d")
                hoje = datetime.now()
                idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
            except:
                pass

        # 1. Busca o ID do time de forma flexível
        time_id_bruto = perfil.get("time_atual_id") or perfil.get("time_id") or perfil.get("team_id")
        
        # 2. Traduz o ID para o Nome Real
        nome_do_time = "N/A"
        if time_id_bruto and str(time_id_bruto).isdigit():
            try:
                time_info = teams.find_team_name_by_id(int(time_id_bruto))
                if time_info:
                    nome_do_time = time_info['full_name'] 
            except Exception:
                nome_do_time = str(time_id_bruto) 
        elif time_id_bruto:
            nome_do_time = str(time_id_bruto)
        
        # 👉 AQUI ESTAVA O ERRO! Agora ele imprime "nome_do_time" em vez do ID.
        st.markdown(f"**Time:** {nome_do_time} &nbsp;&nbsp;|&nbsp;&nbsp; **Camisa:** #{camisa} &nbsp;&nbsp;|&nbsp;&nbsp; **Posição:** {posicao}")
        st.markdown(f"**Idade:** {idade} anos &nbsp;&nbsp;|&nbsp;&nbsp; **Físico:** {altura} ft, {peso} lbs &nbsp;&nbsp;|&nbsp;&nbsp; **País:** {pais}")
        
        st.caption(f"Analisando dados da temporada **{st.session_state.get('filtro_temporada')}** ({st.session_state.get('filtro_tipo_temporada')})")
        
    st.divider()
    
    # ==========================================
    # SEÇÃO DE ESTATÍSTICAS E KPIs
    # ==========================================
    st.subheader("📊 Player Snapshot & KPIs")
    
    temporada_selecionada = st.session_state.get('filtro_temporada')
    stats = obter_estatisticas_resumo(jogador_id, temporada_selecionada)
    
    if stats:
        # 1. Calculando as métricas tradicionais "Per Game"
        jogos = stats.get("jogos_disputados", 0)
        if jogos > 0:
            ppg = round(stats.get("pontos_totais", 0) / jogos, 1)
            rpg = round(stats.get("rebotes_totais", 0) / jogos, 1)
            apg = round(stats.get("assistencias_totais", 0) / jogos, 1)
        else:
            ppg = rpg = apg = "N/A"
            
        # 2. Formatando as métricas avançadas
        ts_pct_raw = stats.get("ts_pct")
        ts_pct = f"{round(ts_pct_raw * 100, 1)}%" if ts_pct_raw is not None else "N/A"
        
        usg_pct_raw = stats.get("usg_pct")
        usg_pct = f"{round(usg_pct_raw * 100, 1)}%" if usg_pct_raw is not None else "N/A"
        
        net_rating = stats.get("net_rating", "N/A")
        
        # 3. Desenhando os Cards na tela (4 colunas)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PPG", ppg, help="Points Per Game (Pontos por jogo)")
            st.metric("USG%", usg_pct, help="Usage Rate: Estima a porcentagem das posses da equipe finalizadas por este jogador. Volume ofensivo.")
            
        with col2:
            st.metric("RPG", rpg, help="Rebounds Per Game (Rebotes por jogo)")
            st.metric("TS%", ts_pct, help="True Shooting Percentage: Mede a eficiência de pontuação considerando 2 pontos, 3 pontos e lances livres.")
            
        with col3:
            st.metric("APG", apg, help="Assists Per Game (Assistências por jogo)")
            st.metric("Net Rating", net_rating, help="Saldo de pontos da equipe a cada 100 posses de bola com este jogador em quadra.")
            
        with col4:
            pie_raw = stats.get("pie")
            pie_formatado = f"{round(pie_raw * 100, 1)}%" if pie_raw is not None else "N/A"
            
            ast_pct_raw = stats.get("ast_pct")
            ast_pct_formatado = f"{round(ast_pct_raw * 100, 1)}%" if ast_pct_raw is not None else "N/A"
            
            st.metric("PIE", pie_formatado, help="Player Impact Estimate: Métrica da NBA que mede a % de todos os eventos positivos do jogo que foram criados por este jogador.")
            st.metric("AST%", ast_pct_formatado, help="Assist Percentage: Estimativa da porcentagem de cestas dos companheiros que este jogador deu assistência enquanto estava em quadra.")
        
        st.divider()
        
        # ==========================================
        # PLAYER SNAPSHOT (RESUMO + GRÁFICO)
        # ==========================================
        st.markdown("### 📝 Player Snapshot")
        
        dados_liga = obter_dados_liga_avancados(temporada_selecionada)
        lista_usg_liga = [jog.get("usg_pct") for jog in dados_liga]
        lista_ts_liga = [jog.get("ts_pct") for jog in dados_liga]
        
        usg_percentil = calcular_percentil(stats.get("usg_pct"), lista_usg_liga)
        ts_percentil = calcular_percentil(stats.get("ts_pct"), lista_ts_liga)
        texto_resumo = gerar_texto_snapshot(usg_percentil, ts_percentil)
        
        col_resumo, col_grafico = st.columns([1.2, 1])
        
        with col_resumo:
            st.info(f"💡 {texto_resumo}")
            
        with col_grafico:
            if usg_percentil is not None and ts_percentil is not None:
                fig_percentis = grafico_percentis_snapshot(usg_percentil, ts_percentil)
                st.plotly_chart(fig_percentis, use_container_width=True, config={'displayModeBar': False})
            else:
                st.caption("Gráfico indisponível para esta amostra.")
                
        st.divider()

        # ==========================================
        # PLAYER VS LEAGUE (TABELA)
        # ==========================================
        st.subheader("⚖️ Player vs League")
        st.markdown("Comparação do jogador contra a média dos jogadores ativos na temporada. O **Percentil** indica o nível em relação ao resto da liga (ex: 90º significa melhor que 90% dos jogadores).")
        
        df_liga_completo = obter_dados_completos_liga(temporada_selecionada)
        
        if not df_liga_completo.empty:
            df_comparativo = gerar_tabela_comparativa(stats, df_liga_completo)
            st.dataframe(
                df_comparativo,
                use_container_width=True,
                hide_index=True 
            )
        else:
            st.warning("Não foi possível carregar as médias da liga para comparação.")