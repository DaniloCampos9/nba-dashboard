import requests
import time
import pandas as pd
from data.db import supabase
from nba_api.stats.static import teams

# O mesmo dicionário que usamos no painel
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

def atualizar_elencos_via_espn():
    print("--- INICIANDO RASTREAMENTO DE ELENCOS VIA ESPN API ---")
    
    # 1. Puxar todos os jogadores do nosso Supabase para bater os nomes
    print("Baixando base de jogadores do Supabase...")
    resp_jog = supabase.table("jogadores").select("id, nome_completo").execute()
    df_nossos_jogadores = pd.DataFrame(resp_jog.data)
    
    if df_nossos_jogadores.empty:
        print("Erro: Nenhum jogador no banco.")
        return

    # Vamos converter os nomes para minúsculas para facilitar o cruzamento
    df_nossos_jogadores['nome_lower'] = df_nossos_jogadores['nome_completo'].str.lower()
    
    # 2. Obter os times da ESPN
    url_espn_teams = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams?limit=30"
    req = requests.get(url_espn_teams)
    times_espn = req.json()['sports'][0]['leagues'][0]['teams']
    
    atualizacoes_cadastrais = []
    jogadores_nao_encontrados = []

    for item in times_espn:
        time_espn = item['team']
        abrev = time_espn['abbreviation'] # Ex: LAL, BOS
        espn_team_id = time_espn['id']
        nome_time = time_espn['displayName']
        
        # Achar o ID oficial da NBA para esse time usando nossa sigla
        nba_team_info = teams.find_team_by_abbreviation(abrev)
        if not nba_team_info:
            continue
            
        nba_team_id = nba_team_info['id']
        print(f"Lendo elenco: {nome_time} ({abrev})")
        
        # 3. Puxar o roster específico desse time na ESPN
        url_roster = f"http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{espn_team_id}/roster"
        req_roster = requests.get(url_roster)
        
        try:
            atletas = req_roster.json()['athletes']
            for atleta in atletas:
                nome_espn = atleta['fullName'].lower()
                
                # Procura esse nome na nossa base do Supabase
                match = df_nossos_jogadores[df_nossos_jogadores['nome_lower'] == nome_espn]
                
                if not match.empty:
                    nba_player_id = int(match.iloc[0]['id'])
                    atualizacoes_cadastrais.append({
                        "id": nba_player_id,
                        "time_atual_id": nba_team_id
                    })
                else:
                    # Alguns nomes têm sufixos diferentes (ex: Kelly Oubre Jr. vs Kelly Oubre)
                    jogadores_nao_encontrados.append(f"{atleta['fullName']} ({abrev})")
        except KeyError:
            print(f"Erro ao ler os atletas de {nome_time}")
            
        time.sleep(0.5)

    # 4. Enviar para o Supabase
    if atualizacoes_cadastrais:
        print(f"\nSalvando {len(atualizacoes_cadastrais)} jogadores cruzados no Supabase...")
        from carregador import dividir_em_lotes
        for lote in dividir_em_lotes(atualizacoes_cadastrais, 100):
            supabase.table("jogadores").upsert(lote).execute()
        print("✅ ELENCOS ATUALIZADOS COM SUCESSO PELA ESPN!")
        
    if jogadores_nao_encontrados:
        print("\n⚠️ Jogadores ignorados por divergência de nome (Jr., Sr., hífens):")
        for j in jogadores_nao_encontrados[:15]:
            print(f" - {j}")
        print(f"... e mais {len(jogadores_nao_encontrados) - 15} outros.")

if __name__ == "__main__":
    atualizar_elencos_via_espn()