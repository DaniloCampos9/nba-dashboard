import time
from nba_api.stats.endpoints import leaguedashplayerstats
from carregador import supabase, dividir_em_lotes
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def atualizar_3_pontos_no_supabase(lote):
    supabase.table("estatisticas_temporada").upsert(lote).execute()

# Retiramos os headers e colocamos uma espera de 30 SEGUNDOS caso dê erro (tempo pro firewall esfriar)
@retry(stop=stop_after_attempt(4), wait=wait_fixed(30))
def buscar_dados_nba_com_paciencia(temporada, tipo):
    print(f"   ⏳ Conectando aos servidores da NBA para {temporada} ({tipo})...")
    # Usando o padrão nativo da biblioteca, mas com timeout estendido para não dar 'Read timed out'
    return leaguedashplayerstats.LeagueDashPlayerStats(
        season=temporada, 
        season_type_all_star=tipo,
        timeout=60
    ).get_data_frames()[0]

def resgatar_bolas_de_3_passadas():
    # Focando apenas no que faltou
    temporadas = ["2024-25", "2023-24", "2022-23"]
    tipos = ["Regular Season", "Playoffs"]
    
    print("🚀 INICIANDO O RESGATE COM PACIÊNCIA TIBETANA (SEM HEADERS CUSTOMIZADOS)")
    
    for temporada in temporadas:
        for tipo in tipos:
            print(f"\n👉 Puxando {tipo} da temporada {temporada}...")
            try:
                df = buscar_dados_nba_com_paciencia(temporada, tipo)
                
                if df.empty:
                    print("   ℹ️ Nenhum dado encontrado para este corte.")
                    continue
                
                lista_atualizacao = []
                for _, row in df.iterrows():
                    lista_atualizacao.append({
                        "jogador_id": int(row['PLAYER_ID']),
                        "temporada": temporada,
                        "tipo_temporada": tipo,
                        "fg3m_totais": int(row['FG3M']),
                        "fg3a_totais": int(row['FG3A'])
                    })
                
                for lote in dividir_em_lotes(lista_atualizacao, 100):
                    atualizar_3_pontos_no_supabase(lote)
                
                print(f"✅ Atualização de {temporada} ({tipo}) concluída com sucesso!")
                
            except Exception as e:
                print(f"❌ Erro final após todas as tentativas: {e}")
                
            # O segredo: 15 segundos de pausa entre CADA requisição. 
            # Vai demorar uns 2 minutinhos no total, mas passa liso pelo radar.
            print("   💤 Descansando 15 segundos para não alertar a NBA...")
            time.sleep(15) 

if __name__ == "__main__":
    resgatar_bolas_de_3_passadas()