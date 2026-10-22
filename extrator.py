from nba_api.stats.endpoints import (
    commonplayerinfo, playercareerstats, commonallplayers, 
    leaguedashplayerstats, leaguehustlestatsplayer, leaguedashplayerclutch,
    leaguedashteamstats
)
import time
from tenacity import retry, stop_after_attempt, wait_fixed
import pandas as pd

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_dados_brutos_jogador(player_id):
    time.sleep(0.3) 
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    return info.get_dict()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_carreira(player_id):
    time.sleep(0.3)
    carreira = playercareerstats.PlayerCareerStats(player_id=player_id)
    return carreira.get_dict()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_avancadas_liga(temporada="2023-24", tipo="Regular Season"):
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense='Advanced', season=temporada, season_type_all_star=tipo
    )
    return stats.get_dict(), temporada

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_hustle_liga(temporada="2023-24", tipo="Regular Season"):
    stats = leaguehustlestatsplayer.LeagueHustleStatsPlayer(season=temporada, season_type_all_star=tipo)
    return stats.get_dict(), temporada

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_clutch_liga(temporada="2023-24", tipo="Regular Season"):
    stats = leaguedashplayerclutch.LeagueDashPlayerClutch(season=temporada, season_type_all_star=tipo)
    return stats.get_dict(), temporada

def extrair_dados_defesa(temporada_nba, tipo="Regular Season"):
    dados_trad = leaguedashplayerstats.LeagueDashPlayerStats(season=temporada_nba, season_type_all_star=tipo).get_data_frames()[0]
    df_trad = dados_trad[['PLAYER_ID', 'STL', 'BLK']]
    
    dados_hustle = leaguehustlestatsplayer.LeagueHustleStatsPlayer(season=temporada_nba, season_type_all_star=tipo).get_data_frames()[0]
    df_hustle = dados_hustle[['PLAYER_ID', 'DEFLECTIONS']]
    
    df_defesa = pd.merge(df_trad, df_hustle, on='PLAYER_ID', how='inner')
    df_defesa['temporada'] = temporada_nba
    df_defesa['tipo_temporada'] = tipo
    return df_defesa

def extrair_dados_times(temporada_nba, tipo="Regular Season"):
    try:
        dados_times = leaguedashteamstats.LeagueDashTeamStats(
            season=temporada_nba, measure_type_detailed_defense='Advanced', season_type_all_star=tipo
        ).get_data_frames()[0]
        
        df_times = dados_times[['TEAM_ID', 'TEAM_NAME', 'GP', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE']].copy()
        df_times['temporada'] = temporada_nba
        df_times['tipo_temporada'] = tipo
        return df_times
    except Exception as e:
        print(f"Erro na extração de times: {e}")
        return pd.DataFrame()
    
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def extrair_dados_momento(temporada_nba="2026-27", n_jogos=5):
    """Extrai métricas gerais da temporada para a tabela de momento de forma segura."""
    time.sleep(2.0)
    
    # Puxa os dados base de toda a liga
    base_endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
        season=temporada_nba, season_type_all_star="Regular Season", measure_type_detailed_defense="Base", timeout=30
    )
    df_base = base_endpoint.get_data_frames()[0]
    
    time.sleep(2.0)
    
    # Puxa os dados avançados de toda a liga
    adv_endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
        season=temporada_nba, season_type_all_star="Regular Season", measure_type_detailed_defense="Advanced", timeout=30
    )
    df_adv = adv_endpoint.get_data_frames()[0]
    
    if df_base.empty or df_adv.empty:
        return pd.DataFrame()
        
    cols_base = ['PLAYER_ID', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG3M', 'FG3A', 'PLUS_MINUS']
    cols_adv = ['PLAYER_ID', 'TS_PCT', 'EFG_PCT', 'USG_PCT', 'NET_RATING', 'PIE']
    
    df_momento = pd.merge(df_base[cols_base], df_adv[cols_adv], on='PLAYER_ID', how='inner')
    df_momento['temporada'] = temporada_nba
    return df_momento