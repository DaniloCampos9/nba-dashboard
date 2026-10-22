import streamlit as st
import pandas as pd
import io
from data.db import supabase

@st.cache_data(ttl=86400) 
def obter_lista_jogadores():
    try:
        nomes = set()
        inicio = 0
        tamanho_pagina = 1000
        
        while True:
            resp = supabase.table("jogadores").select("nome_completo").range(inicio, inicio + tamanho_pagina - 1).execute()
            
            if not resp.data:
                break
                
            for row in resp.data:
                if row.get('nome_completo'):
                    nomes.add(row['nome_completo'])
            
            if len(resp.data) < tamanho_pagina:
                break
                
            inicio += tamanho_pagina
            
        return sorted(list(nomes))
    except Exception as e:
        print(f"Erro ao carregar lista de jogadores: {e}")
        return []

def obter_perfil_jogador(nome_jogador):
    try:
        resposta = supabase.table("jogadores").select("*").eq("nome_completo", nome_jogador).execute()
        if resposta.data: return resposta.data[0]
        return None
    except Exception: return None

# 🧠 O CÉREBRO DO FILTRO: Traz tudo se for "Ambos", ou filtra se for específico
def aplicar_filtro(query, tipo):
    if tipo != "Regular Season + Playoffs":
        return query.eq("tipo_temporada", tipo)
    return query

@st.cache_data(ttl=300)
def obter_estatisticas_resumo(jogador_id, temporada, tipo="Regular Season"):
    try:
        q_trad = supabase.table("estatisticas_temporada").select("*").eq("jogador_id", jogador_id).eq("temporada", temporada)
        q_adv = supabase.table("stats_avancadas").select("*").eq("jogador_id", jogador_id).eq("temporada", temporada)
        
        resp_trad = aplicar_filtro(q_trad, tipo).execute()
        resp_adv = aplicar_filtro(q_adv, tipo).execute()
        
        stats = {}
        if resp_trad.data:
            df = pd.DataFrame(resp_trad.data)
            stats['jogos_disputados'] = int(df['jogos_disputados'].sum())
            stats['pontos_totais'] = int(df['pontos_totais'].sum())
            stats['rebotes_totais'] = int(df['rebotes_totais'].sum())
            stats['assistencias_totais'] = int(df['assistencias_totais'].sum())
            stats['fg3m_totais'] = int(df['fg3m_totais'].sum()) if 'fg3m_totais' in df.columns else 0
            stats['fg3a_totais'] = int(df['fg3a_totais'].sum()) if 'fg3a_totais' in df.columns else 0
        if resp_adv.data:
            df = pd.DataFrame(resp_adv.data)
            stats['ts_pct'] = df['ts_pct'].mean()
            stats['usg_pct'] = df['usg_pct'].mean()
            stats['net_rating'] = df['net_rating'].mean()
            stats['off_rating'] = df['off_rating'].mean()
            stats['def_rating'] = df['def_rating'].mean()
            stats['pie'] = df['pie'].mean()
            stats['ast_pct'] = df['ast_pct'].mean()
            stats['pace'] = df['pace'].mean()
        return stats
    except Exception: return {}
    
@st.cache_data(ttl=3600)
def obter_dados_liga_avancados(temporada, tipo="Regular Season"):
    try:
        q = supabase.table("stats_avancadas").select("jogador_id, usg_pct, ts_pct").eq("temporada", temporada)
        resp = aplicar_filtro(q, tipo).execute()
        if not resp.data: return []
        df = pd.DataFrame(resp.data)
        return df.groupby("jogador_id").mean().reset_index().to_dict('records')
    except Exception: return []

@st.cache_data(ttl=3600)
def obter_dados_completos_liga(temporada, tipo="Regular Season"):
    try:
        q_trad = supabase.table("estatisticas_temporada").select("jogador_id, jogos_disputados, pontos_totais, rebotes_totais, assistencias_totais").eq("temporada", temporada)
        q_adv = supabase.table("stats_avancadas").select("jogador_id, ts_pct, usg_pct, net_rating, efg_pct, ast_pct").eq("temporada", temporada)
        
        df_trad = pd.DataFrame(aplicar_filtro(q_trad, tipo).execute().data)
        df_adv = pd.DataFrame(aplicar_filtro(q_adv, tipo).execute().data)
        
        if df_trad.empty or df_adv.empty: return pd.DataFrame()
        
        df_trad = df_trad.groupby("jogador_id").sum().reset_index()
        df_adv = df_adv.groupby("jogador_id").mean().reset_index()
        
        df = pd.merge(df_trad, df_adv, on="jogador_id", how="inner")
        df = df[df['jogos_disputados'] > 0].copy()
        df['PPG'] = df['pontos_totais'] / df['jogos_disputados']
        df['RPG'] = df['rebotes_totais'] / df['jogos_disputados']
        df['APG'] = df['assistencias_totais'] / df['jogos_disputados']
        return df
    except Exception: return pd.DataFrame()

@st.cache_data(ttl=3600)
def obter_dados_graficos_ataque(temporada, tipo="Regular Season"):
    try:
        q_trad = supabase.table("estatisticas_temporada").select("jogador_id, jogos_disputados, pontos_totais").eq("temporada", temporada)
        q_adv = supabase.table("stats_avancadas").select("jogador_id, ts_pct, usg_pct").eq("temporada", temporada)
        df_jog = pd.DataFrame(supabase.table("jogadores").select("id, nome_completo").execute().data)

        df_trad = pd.DataFrame(aplicar_filtro(q_trad, tipo).execute().data)
        df_adv = pd.DataFrame(aplicar_filtro(q_adv, tipo).execute().data)

        if df_trad.empty or df_adv.empty or df_jog.empty: return pd.DataFrame()

        df_trad = df_trad.groupby("jogador_id").sum().reset_index()
        df_adv = df_adv.groupby("jogador_id").mean().reset_index()

        df = pd.merge(df_trad, df_adv, on="jogador_id")
        df = pd.merge(df, df_jog, left_on="jogador_id", right_on="id")

        df = df[df['jogos_disputados'] > 0].copy()
        df['PPG'] = round(df['pontos_totais'] / df['jogos_disputados'], 1)
        df['TS%'] = round(df['ts_pct'] * 100, 1)
        df['USG%'] = round(df['usg_pct'] * 100, 1)
        return df
    except Exception: return pd.DataFrame()
    
@st.cache_data(ttl=300)
def obter_estatisticas_defesa(jogador_id, temporada, tipo="Regular Season"):
    try:
        q = supabase.table("stats_defesa").select("*").eq("jogador_id", jogador_id).eq("temporada", temporada)
        resp = aplicar_filtro(q, tipo).execute()
        if not resp.data: return {}
        
        df = pd.DataFrame(resp.data)
        return {
            'roubos_totais': int(df['roubos_totais'].sum()),
            'tocos_totais': int(df['tocos_totais'].sum()),
            'deflections': int(df['deflections'].sum())
        }
    except Exception: return {}
    
@st.cache_data(ttl=300)
def obter_dados_times(temporada, tipo="Regular Season"):
    try:
        q = supabase.table("stats_times").select("*").eq("temporada", temporada)
        resp = aplicar_filtro(q, tipo).execute()
        if not resp.data: return []
        
        df = pd.DataFrame(resp.data)
        df_agg = df.groupby("nome_time").agg({
            'vitorias': 'sum', 'derrotas': 'sum', 'jogos': 'sum',
            'off_rating': 'mean', 'def_rating': 'mean', 'net_rating': 'mean', 'pace': 'mean'
        }).reset_index()
        return df_agg.to_dict('records')
    except Exception: return []

# =========================================================================
# AS DUAS FUNÇÕES ABAIXO FORAM COMPLETAMENTE REFATORADAS PARA USAR SUPABASE
# =========================================================================

@st.cache_data(ttl=3600)
def obter_mapa_arremessos_jogador(jogador_id, temporada, tipo_temporada="Regular Season"):
    """Busca o mapa de arremessos instantaneamente no Supabase Storage (Buckets)."""
    def buscar_por_tipo(tipo_nba):
        caminho = f"{temporada}/{tipo_nba}/{jogador_id}.parquet"
        try:
            bytes_arquivo = supabase.storage.from_("shotcharts").download(caminho)
            df = pd.read_parquet(io.BytesIO(bytes_arquivo))
            
            # === MÁGICA MATEMÁTICA PARA RECRIAR A COLUNA ===
            # Na NBA, o aro fica no centro (0,0) e cada 10 unidades de LOC equivalem a 1 pé (foot).
            # Usamos Pitágoras (a² + b² = c²) para achar a distância exata do arremesso!
            if not df.empty and 'SHOT_DISTANCE' not in df.columns:
                df['SHOT_DISTANCE'] = ((df['LOC_X']**2 + df['LOC_Y']**2) ** 0.5 / 10).round().astype(int)
            # ===============================================
            
            return df
        except Exception:
            return pd.DataFrame()

    if tipo_temporada == "Regular Season + Playoffs":
        df_reg = buscar_por_tipo("Regular Season")
        df_play = buscar_por_tipo("Playoffs")
        df_completo = pd.concat([df_reg, df_play], ignore_index=True)
        return df_completo if not df_completo.empty else pd.DataFrame()
    else:
        return buscar_por_tipo(tipo_temporada)

@st.cache_data(ttl=86400)
def obter_timeline_carreira(jogador_id):
    """Busca a carreira INTEIRA do jogador direto da nossa tabela Postgres no Supabase."""
    try:
        resp = supabase.table("career_stats").select("*").eq("player_id", jogador_id).execute()
        if not resp.data:
            return pd.DataFrame(), pd.DataFrame()
            
        df = pd.DataFrame(resp.data)
        
        # Filtra e organiza os DataFrames exatamente do jeito que a sua interface espera
        df_reg = df[df['tipo_temporada'] == 'Regular Season'].copy()
        df_play = df[df['tipo_temporada'] == 'Playoffs'].copy()
        
        # Ordena pela temporada para o gráfico ficar bonito
        df_reg = df_reg.sort_values(by="season_id")
        df_play = df_play.sort_values(by="season_id")
        
        return df_reg, df_play
    except Exception:
        return pd.DataFrame(), pd.DataFrame()
    
# =========================================================================
# NOVAS FUNÇÕES PARA O ÉPICO 2: ECOSSISTEMA DE TIMES
# =========================================================================

# Dicionário de conversão para cruzar o nome do time com a sigla dos jogadores
TEAM_MAPPING = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS"
}

@st.cache_data(ttl=3600)
def obter_lista_times(temporada):
    """Busca os times únicos disponíveis na temporada selecionada."""
    try:
        resp = supabase.table("stats_times").select("nome_time").eq("temporada", temporada).execute()
        times = list(set([linha['nome_time'] for linha in resp.data if linha.get('nome_time')]))
        
        # 👇 A CORREÇÃO ESTÁ AQUI: Se a lista do banco vier vazia, usamos o dicionário oficial!
        if not times:
            return sorted(list(TEAM_MAPPING.keys()))
            
        return sorted(times)
    except Exception:
        # Fallback de segurança em caso de erro na conexão
        return sorted(list(TEAM_MAPPING.keys()))

@st.cache_data(ttl=3600)
def obter_identidade_time(nome_time, temporada, tipo="Regular Season"):
    """Busca o DNA e as métricas do time na tabela stats_times."""
    try:
        q = supabase.table("stats_times").select("*").eq("nome_time", nome_time).eq("temporada", temporada)
        resp = aplicar_filtro(q, tipo).execute()
        if resp.data:
            return resp.data[0]
        return None
    except Exception: return None

@st.cache_data(ttl=3600)
def obter_elenco_time(nome_time, temporada, tipo="Regular Season"):
    """Cruza a tabela de temporada e jogadores para montar a tabela de rotação avançada (Ordenada por Minutos ou Pontos)."""
    abrev = TEAM_MAPPING.get(nome_time)
    if not abrev: return pd.DataFrame()
    
    try:
        q_trad = supabase.table("estatisticas_temporada").select("jogador_id, jogos_disputados, minutos_totais, pontos_totais, rebotes_totais, assistencias_totais").eq("temporada", temporada).eq("time_abrev", abrev)
        resp_trad = aplicar_filtro(q_trad, tipo).execute()
        
        if not resp_trad.data:
            from nba_api.stats.static import teams
            time_info = teams.find_team_by_abbreviation(abrev)
            if not time_info: return pd.DataFrame()
            
            resp_jog = supabase.table("jogadores").select("id, nome_completo, posicao").eq("time_atual_id", time_info['id']).execute()
            if not resp_jog.data: return pd.DataFrame()
            
            df_jog = pd.DataFrame(resp_jog.data).rename(columns={"id": "jogador_id"})
            for col in ['jogos_disputados', 'MPG', 'PPG', 'RPG', 'APG', 'ts_pct', 'usg_pct', 'net_rating']:
                df_jog[col] = 0.0
            
            ids = df_jog['jogador_id'].tolist()
            resp_past = supabase.table("estatisticas_temporada").select("jogador_id, minutos_totais, jogos_disputados").eq("temporada", "2025-26").in_("jogador_id", ids).execute()
            
            if resp_past.data:
                df_past = pd.DataFrame(resp_past.data)
                df_past = df_past[df_past['jogos_disputados'] > 0].copy()
                df_past['minutos_totais'] = pd.to_numeric(df_past.get('minutos_totais', 0), errors='coerce').fillna(0.0)
                df_past['MPG_past'] = (df_past['minutos_totais'] / df_past['jogos_disputados']).fillna(0.0)
                
                df_jog = pd.merge(df_jog, df_past[['jogador_id', 'MPG_past']], on="jogador_id", how="left").fillna(0)
                return df_jog.sort_values(by=["MPG_past", "PPG"], ascending=[False, False]).drop(columns=['MPG_past']).reset_index(drop=True)
                
            return df_jog

        q_adv = supabase.table("stats_avancadas").select("jogador_id, ts_pct, usg_pct, net_rating").eq("temporada", temporada)
        resp_adv = aplicar_filtro(q_adv, tipo).execute()
        
        df_trad = pd.DataFrame(resp_trad.data)
        df_adv = pd.DataFrame(resp_adv.data) if resp_adv.data else pd.DataFrame()
        
        ids_jogadores = df_trad['jogador_id'].tolist()
        resp_jog = supabase.table("jogadores").select("id, nome_completo, posicao").in_("id", ids_jogadores).execute()
        df_jog = pd.DataFrame(resp_jog.data) if resp_jog.data else pd.DataFrame()
        
        if not df_jog.empty:
            df_trad = df_trad.drop_duplicates(subset=['jogador_id'])
            df_adv = df_adv.drop_duplicates(subset=['jogador_id'])
            df_jog = df_jog.drop_duplicates(subset=['id'])

            df = pd.merge(df_trad, df_jog, left_on="jogador_id", right_on="id")
            if not df_adv.empty:
                df = pd.merge(df, df_adv, on="jogador_id", how="left")
                
            df = df[df['jogos_disputados'] > 0].copy()
            
            # TRATAMENTO ROBUSTO CONTRA NAN
            if 'minutos_totais' not in df.columns:
                df['minutos_totais'] = 0.0
            
            df['minutos_totais'] = pd.to_numeric(df['minutos_totais'], errors='coerce').fillna(0.0)
            df['MPG'] = (df['minutos_totais'] / df['jogos_disputados']).round(1).fillna(0.0)
            
            df['PPG'] = (df['pontos_totais'] / df['jogos_disputados']).round(1).fillna(0.0)
            df['RPG'] = (df['rebotes_totais'] / df['jogos_disputados']).round(1).fillna(0.0)
            df['APG'] = (df['assistencias_totais'] / df['jogos_disputados']).round(1).fillna(0.0)
            
            for col in ['ts_pct', 'usg_pct', 'net_rating']:
                if col not in df.columns: df[col] = 0.0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
                    
            # ORDENAÇÃO SEGURA: Primeiro por Minutos, depois por Pontos
            return df.sort_values(by=["MPG", "PPG"], ascending=[False, False]).reset_index(drop=True)
            
        return pd.DataFrame()
    except Exception as e: 
        print(f"Erro obter_elenco_time: {e}")
        return pd.DataFrame()
    
@st.cache_data(ttl=300)
def obter_hot_streaks_supabase(temporada="2026-27"):
    """Busca os dados dos últimos 5 jogos no Supabase e cruza com a temporada atual e clutch."""
    try:
        resp_mom = supabase.table("stats_momento").select("*").eq("temporada", temporada).execute()
        if not resp_mom.data:
            return pd.DataFrame(), pd.DataFrame()
            
        df_mom = pd.DataFrame(resp_mom.data)
        
        # Busca nomes dos jogadores
        ids = df_mom['jogador_id'].tolist()
        resp_jog = supabase.table("jogadores").select("id, nome_completo, posicao").in_("id", ids).execute()
        df_jog = pd.DataFrame(resp_jog.data) if resp_jog.data else pd.DataFrame()
        
        # Busca médias da temporada atual para calcular o Delta (Quem mais esquentou)
        resp_temp = supabase.table("estatisticas_temporada").select("jogador_id, jogos_disputados, pontos_totais").eq("temporada", temporada).eq("tipo_temporada", "Regular Season").execute()
        df_temp = pd.DataFrame(resp_temp.data) if resp_temp.data else pd.DataFrame()
        
        # Busca dados de Clutch da temporada atual no banco
        resp_clutch = supabase.table("stats_clutch").select("*").eq("temporada", temporada).eq("tipo_temporada", "Regular Season").execute()
        df_clutch = pd.DataFrame(resp_clutch.data) if resp_clutch.data else pd.DataFrame()

        df = pd.merge(df_mom, df_jog, left_on="jogador_id", right_on="id", how="inner")
        df = df[df['gp'] > 0].copy()
        
        # Médias por jogo na janela recente (Sem filtro mínimo de jogos!)
        df['PPG'] = (df['pts'] / df['gp']).round(1)
        df['RPG'] = (df['reb'] / df['gp']).round(1)
        df['APG'] = (df['ast'] / df['gp']).round(1)
        df['SPG'] = (df['stl'] / df['gp']).round(1)
        df['BPG'] = (df['blk'] / df['gp']).round(1)
        df['STOCKS'] = (df['SPG'] + df['BPG']).round(1)
        df['MPG'] = (df['minutos'] / df['gp']).round(1)
        df['3PM'] = (df['fg3m'] / df['gp']).round(1)
        df['3P%'] = ((df['fg3m'] / df['fg3a'].replace(0, pd.NA)) * 100).fillna(0.0).round(1)
        df['PLUS_MINUS_PG'] = (df['plus_minus'] / df['gp']).round(1)
        
        df['TS%'] = (df['ts_pct'] * 100).round(1)
        df['USG%'] = (df['usg_pct'] * 100).round(1)
        df['PIE%'] = (df['pie'] * 100).round(1)
        
        # Cálculo do Delta de Temperatura (PPG últimos 5 jogos vs PPG Temporada)
        if not df_temp.empty:
            df_temp = df_temp[df_temp['jogos_disputados'] > 0].copy()
            df_temp['PPG_SEASON'] = (df_temp['pontos_totais'] / df_temp['jogos_disputados']).round(1)
            df = pd.merge(df, df_temp[['jogador_id', 'PPG_SEASON']], on="jogador_id", how="left")
            df['DELTA_PPG'] = (df['PPG'] - df['PPG_SEASON'].fillna(df['PPG'])).round(1)
        else:
            df['PPG_SEASON'] = df['PPG']
            df['DELTA_PPG'] = 0.0

        # Prepara DataFrame de Clutch com nomes
        if not df_clutch.empty and not df_jog.empty:
            df_clutch = pd.merge(df_clutch, df_jog, left_on="jogador_id", right_on="id", how="inner")
            df_clutch['CLUTCH_FG%'] = (df_clutch['clutch_fg_pct'].fillna(0) * 100).round(1)
            df_clutch['CLUTCH_3P%'] = (df_clutch['clutch_3p_pct'].fillna(0) * 100).round(1)
            df_clutch['CLUTCH_USG%'] = (df_clutch['clutch_usg_pct'].fillna(0) * 100).round(1)

        return df, df_clutch
    except Exception as e:
        print(f"Erro ao buscar Hot Streaks no Supabase: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=3600)
def obter_benchmarking_jogador(jogador_id, temporada, tipo="Regular Season"):
    """Calcula o percentil e a classificação do jogador em relação ao resto da liga."""
    df_liga = obter_dados_completos_liga(temporada, tipo)
    if df_liga.empty: return None

    # Filtro: Ignora quem jogou menos de 10 jogos para não distorcer as médias da liga
    df_valida = df_liga[df_liga['jogos_disputados'] >= 10].copy()
    if df_valida.empty or jogador_id not in df_valida['jogador_id'].values: return None

    jogador_stats = df_valida[df_valida['jogador_id'] == jogador_id].iloc[0]
    
    benchmarks = {}
    metricas = {
        'PPG': ('Pontos', False), 'RPG': ('Rebotes', False), 'APG': ('Assistências', False), 
        'ts_pct': ('True Shooting', True), 'usg_pct': ('Usage Rate', True), 
        'net_rating': ('Net Rating', False), 'pie': ('PIE', True), 'ast_pct': ('AST%', True)
    }
    
    for coluna, (nome_amigavel, is_pct) in metricas.items():
        if coluna not in df_valida.columns: continue
        
        valor = jogador_stats[coluna]
        media_liga = df_valida[coluna].mean()
        percentil = (df_valida[coluna] < valor).mean() * 100
        
        if percentil >= 90: classif, cor = "🌟 Elite", "normal"
        elif percentil >= 75: classif, cor = "📈 Acima Média", "normal"
        elif percentil >= 40: classif, cor = "📊 Na Média", "off"
        else: classif, cor = "📉 Abaixo Média", "inverse"
            
        benchmarks[coluna] = {
            "nome": nome_amigavel,
            "valor": valor * 100 if is_pct else valor,
            "media_liga": media_liga * 100 if is_pct else media_liga,
            "percentil": percentil,
            "classificacao": classif,
            "cor": cor,
            "is_pct": is_pct
        }
    return benchmarks

@st.cache_data(ttl=3600)
def obter_hot_streaks_liga(temporada="2026-27"):
    """Busca o desempenho da liga inteira nos últimos 10 jogos (Base e Avançado)."""
    from nba_api.stats.endpoints import leaguedashplayerstats
    import pandas as pd
    
    try:
        # Puxa estatísticas tradicionais (Pontos, Roubos, Tocos)
        df_base = leaguedashplayerstats.LeagueDashPlayerStats(
            season=temporada, last_n_games=10, measure_type_detailed_defense="Base"
        ).get_data_frames()[0]
        
        # Puxa estatísticas avançadas (TS%, Net Rating, PIE)
        df_adv = leaguedashplayerstats.LeagueDashPlayerStats(
            season=temporada, last_n_games=10, measure_type_detailed_defense="Advanced"
        ).get_data_frames()[0]
        
        if df_base.empty or df_adv.empty: return pd.DataFrame()
        
        # Junta tudo usando o ID do jogador
        df_completo = pd.merge(
            df_base[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PTS', 'STL', 'BLK']], 
            df_adv[['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'NET_RATING', 'PIE']], 
            on='PLAYER_ID'
        )
        
        # Filtro de relevância: Apenas quem jogou pelo menos 5 dos últimos 10 jogos e mais de 15 min/jogo
        df_valido = df_completo[(df_completo['GP'] >= 5) & (df_completo['MIN'] >= 15)].copy()
        
        # Normaliza para médias por jogo
        df_valido['PPG'] = df_valido['PTS'] / df_valido['GP']
        df_valido['SPG'] = df_valido['STL'] / df_valido['GP']
        df_valido['BPG'] = df_valido['BLK'] / df_valido['GP']
        
        return df_valido
    except Exception as e:
        print(f"Erro ao buscar Hot Streaks: {e}")
        return pd.DataFrame()