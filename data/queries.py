import streamlit as st
import pandas as pd
from data.db import supabase

@st.cache_data(ttl=3600)
def obter_lista_jogadores():
    try:
        resposta = supabase.table("jogadores").select("nome_completo").execute()
        jogadores = [linha['nome_completo'] for linha in resposta.data if linha.get('nome_completo')]
        return sorted(jogadores)
    except Exception as e:
        return ["Erro ao carregar"]

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
        if resp_adv.data:
            df = pd.DataFrame(resp_adv.data)
            stats['ts_pct'] = df['ts_pct'].mean()
            stats['usg_pct'] = df['usg_pct'].mean()
            stats['net_rating'] = df['net_rating'].mean()
            stats['pie'] = df['pie'].mean()
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

@st.cache_data(ttl=3600)
def obter_mapa_arremessos_jogador(jogador_id, temporada, tipo_temporada="Regular Season"):
    from nba_api.stats.endpoints import shotchartdetail
    import pandas as pd
    try:
        def buscar_por_tipo(tipo_nba):
            return shotchartdetail.ShotChartDetail(
                team_id=0, player_id=jogador_id, context_measure_simple='FGA',
                season_nullable=temporada, season_type_all_star=tipo_nba
            ).get_data_frames()[0]

        if tipo_temporada == "Regular Season + Playoffs":
            return pd.concat([buscar_por_tipo("Regular Season"), buscar_por_tipo("Playoffs")], ignore_index=True)
        return buscar_por_tipo(tipo_temporada)
    except Exception: return pd.DataFrame()
    
    
@st.cache_data(ttl=86400) # Cache de 24h pois histórico passado não muda
def obter_timeline_carreira(jogador_id):
    """Busca a carreira INTEIRA do jogador (todos os anos e times) direto da API da NBA."""
    from nba_api.stats.endpoints import playercareerstats
    import pandas as pd
    
    try:
        carreira = playercareerstats.PlayerCareerStats(player_id=jogador_id)
        df_reg = carreira.get_data_frames()[0] # Temporada Regular
        df_play = carreira.get_data_frames()[2] # Playoffs
        return df_reg, df_play
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()