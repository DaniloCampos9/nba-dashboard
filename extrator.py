from nba_api.stats.endpoints import (
    commonplayerinfo, 
    playercareerstats, 
    commonallplayers, 
    leaguedashplayerstats, 
    leaguehustlestatsplayer, 
    leaguedashplayerclutch,
    leaguedashteamstats  # 👉 Aqui está o import que faltava para os times!
)
import time
from tenacity import retry, stop_after_attempt, wait_fixed
import pandas as pd

# Tenta 3 vezes, esperando 5 segundos entre cada tentativa caso falhe
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_dados_brutos_jogador(player_id):
    print(f"Buscando dados do ID {player_id}...")
    time.sleep(0.3) 
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    return info.get_dict()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_carreira(player_id):
    print(f"Buscando histórico de temporadas do ID {player_id}...")
    time.sleep(0.3)
    carreira = playercareerstats.PlayerCareerStats(player_id=player_id)
    return carreira.get_dict()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_avancadas_liga(temporada="2023-24"):
    print(f"Buscando estatísticas avançadas da liga para a temporada {temporada}...")
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense='Advanced',
        season=temporada
    )
    return stats.get_dict(), temporada

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_hustle_liga(temporada="2023-24"):
    print(f"Buscando estatísticas de Hustle para a temporada {temporada}...")
    stats = leaguehustlestatsplayer.LeagueHustleStatsPlayer(season=temporada)
    return stats.get_dict(), temporada

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def buscar_estatisticas_clutch_liga(temporada="2023-24"):
    print(f"Buscando estatísticas Clutch para a temporada {temporada}...")
    stats = leaguedashplayerclutch.LeagueDashPlayerClutch(season=temporada)
    return stats.get_dict(), temporada


def extrair_dados_defesa(temporada_nba):
    """Busca dados tradicionais de defesa e estatísticas de Hustle da NBA."""
    print(f"Extraindo dados de defesa da temporada {temporada_nba}...")
    
    # 1. Busca Roubos (STL) e Tocos (BLK)
    dados_trad = leaguedashplayerstats.LeagueDashPlayerStats(season=temporada_nba).get_data_frames()[0]
    df_trad = dados_trad[['PLAYER_ID', 'STL', 'BLK']]
    
    # 2. Busca os Deflections (Esforço/Hustle)
    dados_hustle = leaguehustlestatsplayer.LeagueHustleStatsPlayer(season=temporada_nba).get_data_frames()[0]
    df_hustle = dados_hustle[['PLAYER_ID', 'DEFLECTIONS']]
    
    # 3. Mescla os dois bancos usando o ID do jogador
    df_defesa = pd.merge(df_trad, df_hustle, on='PLAYER_ID', how='inner')
    df_defesa['temporada'] = temporada_nba
    
    return df_defesa

def extrair_dados_times(temporada_nba):
    """Busca estatísticas avançadas de todos os times (Ratings, Pace, W/L)."""
    print(f"Extraindo dados dos times da temporada {temporada_nba}...")
    
    try:
        # measure_type_detailed_defense='Advanced' traz as métricas de eficiência por posse de bola
        dados_times = leaguedashteamstats.LeagueDashTeamStats(
            season=temporada_nba,
            measure_type_detailed_defense='Advanced'
        ).get_data_frames()[0]
        
        # Filtramos apenas as colunas que criamos no Supabase
        df_times = dados_times[['TEAM_ID', 'TEAM_NAME', 'GP', 'W', 'L', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE']].copy()
        df_times['temporada'] = temporada_nba
        
        return df_times
    except Exception as e:
        print(f"Erro na extração de times: {e}")
        return pd.DataFrame()