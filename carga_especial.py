import pandas as pd
import time
import io
from supabase import create_client
from nba_api.stats.endpoints import shotchartdetail, playercareerstats

SUPABASE_URL = "https://qqtvqrlrcgctngghwvfd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHZxcmxyY2djdG5nZ2h3dmZkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDYyMzAyMywiZXhwIjoyMTA2MTk5MDIzfQ.7BRJMTOpv4aSAHwo-iPzdQHE7Yd1bpyXfZPMHoMmUF0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

def carga_carreira_e_arremessos():
    print("🚀 Iniciando extração definitiva (Retomando do 27º jogador)...")
    
    resp = sb.table("jogadores").select("id, nome_completo").execute()
    jogadores = resp.data
    
    # Vamos começar do índice 26 (que é o 27º jogador da lista real)
    # Se quiser começar do começo um dia, é só mudar para 0
    JOGADOR_INICIAL = 560
    jogadores_restantes = jogadores[JOGADOR_INICIAL:]
    
    temporadas = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
    
    for idx, jogador in enumerate(jogadores_restantes):
        player_id = jogador['id']
        nome = jogador['nome_completo']
        
        numero_real = JOGADOR_INICIAL + idx + 1
        print(f"\n[{numero_real}/{len(jogadores)}] Baixando dados de {nome}...")
        
        # ==========================================
        # 1. CARREIRA (Postgres)
        # ==========================================
        tentativas_carreira = 0
        while tentativas_carreira < 3:
            try:
                time.sleep(1.5) # Pausa levemente maior para não irritar o firewall
                carreira = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=30)
                
                # Temporada Regular
                df_reg = carreira.get_data_frames()[0]
                if not df_reg.empty:
                    df_reg = df_reg[['PLAYER_ID', 'SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB']].copy()
                    df_reg.columns = ['player_id', 'season_id', 'team_abbreviation', 'gp', 'pts', 'ast', 'reb']
                    df_reg['tipo_temporada'] = 'Regular Season'
                    sb.table("career_stats").upsert(df_reg.to_dict('records')).execute()
                    
                # Playoffs
                df_play = carreira.get_data_frames()[2]
                if not df_play.empty:
                    df_play = df_play[['PLAYER_ID', 'SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'PTS', 'AST', 'REB']].copy()
                    df_play.columns = ['player_id', 'season_id', 'team_abbreviation', 'gp', 'pts', 'ast', 'reb']
                    df_play['tipo_temporada'] = 'Playoffs'
                    sb.table("career_stats").upsert(df_play.to_dict('records')).execute()
                    
                print(f"  ✅ Carreira salva no Postgres.")
                break # Deu certo, sai do loop de tentativas
                
            except Exception as e:
                tentativas_carreira += 1
                if tentativas_carreira < 3:
                    print(f"  ⏳ Tropeço na carreira. Respirando 5s para tentar de novo...")
                    time.sleep(5)
                else:
                    print(f"  ❌ Erro definitivo na carreira de {nome}: {e}")

        # ==========================================
        # 2. SHOT CHARTS (Storage em Parquet)
        # ==========================================
        for season in temporadas:
            for tipo_temp in ["Regular Season", "Playoffs"]:
                tentativas_shots = 0
                while tentativas_shots < 3:
                    try:
                        time.sleep(1.5)
                        resp_shots = shotchartdetail.ShotChartDetail(
                            team_id=0, player_id=player_id, season_nullable=season,
                            season_type_all_star=tipo_temp, context_measure_simple="FGA", timeout=30
                        )
                        df_shots = resp_shots.get_data_frames()[0]
                        
                        if not df_shots.empty:
                            df_shots = df_shots[["GAME_ID", "PERIOD", "LOC_X", "LOC_Y", "SHOT_MADE_FLAG", "SHOT_TYPE", "ACTION_TYPE"]]
                            
                            buf = io.BytesIO()
                            df_shots.to_parquet(buf, index=False, engine='pyarrow', compression='snappy')
                            
                            caminho_arquivo = f"{season}/{tipo_temp}/{player_id}.parquet"
                            
                            sb.storage.from_("shotcharts").upload(
                                path=caminho_arquivo,
                                file=buf.getvalue(),
                                file_options={"upsert": "true", "content-type": "application/octet-stream"}
                            )
                            print(f"  🏀 Shot Chart {season} ({tipo_temp}) salvo no Storage.")
                        
                        break # Se chegou aqui sem erro (com ou sem arremessos), sai do loop de tentativas
                        
                    except Exception as e:
                        erro_str = str(e)
                        # Se for erro de JSON Vazio (Bloqueio) ou Timeout, nós tentamos de novo
                        if "Expecting value" in erro_str or "Timeout" in erro_str or "Read timed out" in erro_str:
                            tentativas_shots += 1
                            if tentativas_shots < 3:
                                print(f"  ⏳ NBA bloqueou {season} ({tipo_temp}). Respirando 5s para tentar de novo...")
                                time.sleep(5)
                            else:
                                print(f"  ⚠ Desistindo de {season} ({tipo_temp}) após 3 tentativas.")
                        else:
                            # Se for outro tipo de erro (ex: jogador não jogou na liga ainda), ignora e segue
                            break

if __name__ == "__main__":
    carga_carreira_e_arremessos()
    print("\n🚀 CARGA FINALIZADA COM SUCESSO!")