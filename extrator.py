from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, commonallplayers, leaguedashplayerstats, leaguehustlestatsplayer, leaguedashplayerclutch
import time
from tenacity import retry, stop_after_attempt, wait_fixed

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