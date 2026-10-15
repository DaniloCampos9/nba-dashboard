import time
import random
import pandas as pd
from supabase import create_client
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats, playerawards, commonallplayers

# Evita o aviso do pandas
pd.set_option('future.no_silent_downcasting', True)

# Conexão direta com o Supabase
URL = "https://qqtvqrlrcgctngghwvfd.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHZxcmxyY2djdG5nZ2h3dmZkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDYyMzAyMywiZXhwIjoyMTA2MTk5MDIzfQ.7BRJMTOpv4aSAHwo-iPzdQHE7Yd1bpyXfZPMHoMmUF0"

supabase = create_client(URL, KEY)

def converter_para_inteiro(valor):
    if valor is None or str(valor).strip() == "": return 0
    try: return int(float(valor))
    except: return 0

def obter_ids_ja_registados():
    """Busca APENAS os IDs que já estão na tabela E que possuem dados reais preenchidos."""
    print("🔍 A verificar jogadores já salvos e validados na base de dados...")
    ids_completos = set()
    try:
        # Fazemos paginação para garantir que lemos os 5000+ jogadores (o Supabase limita a 1000 por padrão)
        inicio = 0
        tamanho_pagina = 1000
        
        while True:
            # Puxamos o ID e um campo que comprove que a bio foi feita (ex: altura_pes)
            resp = supabase.table("jogadores").select("id, altura_pes").range(inicio, inicio + tamanho_pagina - 1).execute()
            
            if not resp.data:
                break
                
            for row in resp.data:
                # SÓ adiciona à lista de 'saltar' se a altura NÃO for nula
                if row.get('altura_pes') is not None and str(row.get('altura_pes')).strip() != "":
                    ids_completos.add(row['id'])
            
            if len(resp.data) < tamanho_pagina:
                break
            
            inicio += tamanho_pagina
            
        return ids_completos
    except Exception as e:
        print(f"Erro ao verificar Supabase: {e}")
    return set()

def executar_carga_otimizada():
    print("🚀 INICIANDO CARGA EM MASSA INTELIGENTE (COM SKIP DE JÁ SALVOS)...")
    
    # Puxa a lista completa da NBA
    df_todos = commonallplayers.CommonAllPlayers(is_only_current_season=0).get_data_frames()[0]
    jogadores = df_todos.to_dict('records')
    total = len(jogadores)
    
    ids_salvos = obter_ids_ja_registados()
    print(f"📊 Total na NBA: {total} | Já salvos no Supabase: {len(ids_salvos)}")

    for idx, jogador in enumerate(jogadores):
        player_id = jogador['PERSON_ID']
        nome = jogador['DISPLAY_FIRST_LAST']
        
        # Otimização de tempo: Se já tem bio, não gasta pedidos à API da NBA!
        if player_id in ids_salvos:
            continue
            
        print(f"\n[{idx+1}/{total}] A processar novo atleta: {nome} (ID: {player_id})")
        
        # ==========================================
        # 1. BIOGRAFIA & PRÊMIOS
        # ==========================================
        sucesso_bio = False
        tentativas_bio = 0
        while tentativas_bio < 3 and not sucesso_bio:
            try:
                time.sleep(random.uniform(4.0, 7.0)) # Pausa moderada e segura
                info_df = commonplayerinfo.CommonPlayerInfo(player_id=player_id, timeout=35).get_data_frames()[0]
                
                time.sleep(random.uniform(2.0, 4.0)) 
                premios_df = playerawards.PlayerAwards(player_id=player_id, timeout=35).get_data_frames()[0]
                
                campeonatos = mvp = dpoy = mip = all_star = fmvp = roy = smoy = all_nba = all_defensive = 0
                
                if not premios_df.empty:
                    campeonatos = len(premios_df[premios_df['DESCRIPTION'] == 'NBA Champion'])
                    mvp = len(premios_df[premios_df['DESCRIPTION'] == 'NBA Most Valuable Player'])
                    dpoy = len(premios_df[premios_df['DESCRIPTION'] == 'NBA Defensive Player of the Year'])
                    mip = len(premios_df[premios_df['DESCRIPTION'] == 'NBA Most Improved Player'])
                    all_star = len(premios_df[premios_df['DESCRIPTION'] == 'NBA All-Star'])
                    fmvp = len(premios_df[premios_df['DESCRIPTION'] == 'NBA Finals Most Valuable Player'])
                    roy = len(premios_df[premios_df['DESCRIPTION'] == 'NBA Rookie of the Year'])
                    smoy = len(premios_df[premios_df['DESCRIPTION'] == 'NBA Sixth Man of the Year'])
                    all_nba = len(premios_df[premios_df['DESCRIPTION'] == 'All-NBA'])
                    all_defensive = len(premios_df[premios_df['DESCRIPTION'] == 'All-Defensive Team'])

                if not info_df.empty:
                    info = info_df.iloc[0]
                    dados_bio = {
                        "id": player_id,
                        "nome_completo": nome, 
                        "data_nascimento": str(info['BIRTHDATE'])[:10] if info['BIRTHDATE'] else None,
                        "pais": info['COUNTRY'],
                        "altura_pes": info['HEIGHT'],
                        "peso_lbs": converter_para_inteiro(info['WEIGHT']),
                        "camisa": info['JERSEY'],
                        "posicao": info['POSITION'],
                        "ano_draft": info['DRAFT_YEAR'],
                        "campeonatos": campeonatos, "mvp": mvp, "dpoy": dpoy,
                        "mip": mip, "all_star": all_star, "fmvp": fmvp,
                        "roy": roy, "smoy": smoy, "all_nba": all_nba,
                        "all_defensive": all_defensive
                    }
                    supabase.table("jogadores").upsert(dados_bio).execute()
                    print(f"  ✅ Bio + Prêmios salvos ({campeonatos} Títulos, {mvp} MVPs).")
                    sucesso_bio = True
            except Exception as e:
                tentativas_bio += 1
                tempo_espera = tentativas_bio * 20
                print(f"  ⏳ [Bio] Bloqueio detetado. A aguardar {tempo_espera}s...")
                time.sleep(tempo_espera)
                
        # ==========================================
        # 2. ESTATÍSTICAS GERAIS DE CARREIRA
        # ==========================================
        sucesso_carreira = False
        tentativas_carreira = 0
        while tentativas_carreira < 3 and not sucesso_carreira:
            try:
                time.sleep(random.uniform(3.0, 5.0)) 
                carreira = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=35)
                
                # Regular Season
                df_reg = carreira.get_data_frames()[0]
                if not df_reg.empty:
                    df_reg = df_reg[['PLAYER_ID', 'SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB']].copy()
                    df_reg.columns = ['player_id', 'season_id', 'team_abbreviation', 'gp', 'pts', 'ast', 'reb']
                    df_reg['tipo_temporada'] = 'Regular Season'
                    df_reg = df_reg.fillna(0)
                    
                    supabase.table("career_stats").upsert(
                        df_reg.to_dict('records'), 
                        on_conflict="player_id, season_id, team_abbreviation, tipo_temporada"
                    ).execute()
                    
                # Playoffs
                df_play = carreira.get_data_frames()[2]
                if not df_play.empty:
                    df_play = df_play[['PLAYER_ID', 'SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB']].copy()
                    df_play.columns = ['player_id', 'season_id', 'team_abbreviation', 'gp', 'pts', 'ast', 'reb']
                    df_play['tipo_temporada'] = 'Playoffs'
                    df_play = df_play.fillna(0)
                    
                    supabase.table("career_stats").upsert(
                        df_play.to_dict('records'), 
                        on_conflict="player_id, season_id, team_abbreviation, tipo_temporada"
                    ).execute()
                    
                print("  ✅ Estatísticas de carreira salvas.")
                sucesso_carreira = True
                
            except Exception as e:
                tentativas_carreira += 1
                tempo_espera = tentativas_carreira * 25
                print(f"  ⏳ [Carreira] A aguardar {tempo_espera}s para nova tentativa...")
                time.sleep(tempo_espera)

    print("\n🎉 CARGA COMPLETA FINALIZADA COM SUCESSO!")

if __name__ == "__main__":
    executar_carga_otimizada()