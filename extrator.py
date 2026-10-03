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