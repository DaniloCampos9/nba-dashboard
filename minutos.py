import time
from supabase import create_client
from nba_api.stats.endpoints import leaguedashplayerstats

# Credenciais diretas
URL = "https://qqtvqrlrcgctngghwvfd.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHZxcmxyY2djdG5nZ2h3dmZkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDYyMzAyMywiZXhwIjoyMTA2MTk5MDIzfQ.7BRJMTOpv4aSAHwo-iPzdQHE7Yd1bpyXfZPMHoMmUF0"
supabase = create_client(URL, KEY)

def dividir_em_lotes(lista, tamanho=100):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i + tamanho]

def atualizar_minutos_definitivo():
    print("🚀 INICIANDO CORREÇÃO DE MINUTOS (COM PROTEÇÃO ANTI-TIMEOUT)...")
    temporadas = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
    tipos = ["Regular Season", "Playoffs"]
    
    for temp in temporadas:
        for tipo in tipos:
            print(f"\n📥 1. Baixando dados de {temp} ({tipo}) da NBA...")
            
            # Tenta descarregar até 3 vezes antes de desistir
            tentativas = 0
            df = None
            while tentativas < 3:
                try:
                    df = leaguedashplayerstats.LeagueDashPlayerStats(
                        season=temp, season_type_all_star=tipo, timeout=30
                    ).get_data_frames()[0]
                    break # Sucesso! Sai do loop de tentativas
                except Exception as e:
                    tentativas += 1
                    print(f"  ⏳ NBA demorou a responder. Tentativa {tentativas}/3. Aguardando 5s...")
                    time.sleep(5)
            
            # Se falhou as 3 vezes ou não tem dados, passa à frente sem apagar nada
            if df is None or df.empty:
                print(f"  ⏭️ Ignorando {temp} ({tipo}) por falta de resposta da API.")
                continue
                
            lista_trad = []
            for _, row in df.iterrows():
                lista_trad.append({
                    "jogador_id": int(row['PLAYER_ID']),
                    "temporada": temp,
                    "tipo_temporada": tipo,
                    "time_abrev": row['TEAM_ABBREVIATION'],
                    "idade": int(row['AGE']),
                    "jogos_disputados": int(row['GP']),
                    "minutos_totais": float(row['MIN']),
                    "pontos_totais": int(row['PTS']),
                    "assistencias_totais": int(row['AST']),
                    "rebotes_totais": int(row['REB']),
                    "fg3m_totais": int(row['FG3M']),
                    "fg3a_totais": int(row['FG3A'])
                })
            
            if lista_trad:
                print(f"🗑️ 2. Download concluído! Limpando dados antigos...")
                try:
                    supabase.table("estatisticas_temporada").delete().eq("temporada", temp).eq("tipo_temporada", tipo).execute()
                except Exception as e:
                    print(f"  ❌ Erro ao limpar o Supabase: {e}")
                
                print(f"💾 3. Inserindo {len(lista_trad)} registos com os minutos corrigidos...")
                try:
                    for lote in dividir_em_lotes(lista_trad, 100):
                        supabase.table("estatisticas_temporada").insert(lote).execute()
                    print(f"  ✅ {temp} ({tipo}) atualizado com sucesso absoluto!")
                except Exception as e:
                    print(f"  ❌ Erro de inserção: {e}")
                    
            time.sleep(3) # Pausa amigável entre requisições
            
    print("\n🎉 PROCESSO CONCLUÍDO!")

if __name__ == "__main__":
    atualizar_minutos_definitivo()