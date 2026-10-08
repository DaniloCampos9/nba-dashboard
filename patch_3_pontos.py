import time
from nba_api.stats.endpoints import playercareerstats
from carregador import supabase, dividir_em_lotes

def montar_payload(row, temporada, tipo):
    """Reconstrói a linha completa para garantir um upsert perfeito."""
    return {
        "jogador_id": int(row['PLAYER_ID']),
        "temporada": temporada,
        "tipo_temporada": tipo,
        "time_abrev": row['TEAM_ABBREVIATION'],
        "idade": int(row['PLAYER_AGE']),
        "jogos_disputados": int(row['GP']),
        "pontos_totais": int(row['PTS']),
        "assistencias_totais": int(row['AST']),
        "rebotes_totais": int(row['REB']),
        "fg3m_totais": int(row['FG3M']),
        "fg3a_totais": int(row['FG3A'])
    }

def resgatar_bolas_de_3_via_carreira():
    print("🚀 INICIANDO RESGATE VIA HISTÓRICO DE CARREIRA (MÉTODO SHOT CHART)")
    
    # 1. Busca os IDs diretamente do banco local
    resp = supabase.table("jogadores").select("id, nome_completo").execute()
    jogadores = resp.data
    
    # 2. Filtros exatos das pendências
    alvos = {
        "2024-25": ["Playoffs"],
        "2023-24": ["Regular Season", "Playoffs"],
        "2022-23": ["Regular Season", "Playoffs"]
    }
    
    lista_atualizacao = []
    
    for idx, jogador in enumerate(jogadores):
        player_id = jogador['id']
        nome = jogador['nome_completo']
        
        print(f"[{idx+1}/{len(jogadores)}] A extrair carreira de {nome}...")
        
        tentativas = 0
        while tentativas < 3:
            try:
                # Pausa idêntica à do carga_especial.py para não acionar o firewall
                time.sleep(1.5)
                
                carreira = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=30)
                
                df_reg = carreira.get_data_frames()[0]  # Regular Season
                df_play = carreira.get_data_frames()[2] # Playoffs
                
                # Procura as temporadas alvo na Regular Season
                if not df_reg.empty:
                    for _, row in df_reg.iterrows():
                        temporada = row['SEASON_ID']
                        if temporada in alvos and "Regular Season" in alvos[temporada]:
                            lista_atualizacao.append(montar_payload(row, temporada, "Regular Season"))
                            
                # Procura as temporadas alvo nos Playoffs
                if not df_play.empty:
                    for _, row in df_play.iterrows():
                        temporada = row['SEASON_ID']
                        if temporada in alvos and "Playoffs" in alvos[temporada]:
                            lista_atualizacao.append(montar_payload(row, temporada, "Playoffs"))
                            
                break # Sucesso, sai do loop de tentativas
                
            except Exception as e:
                tentativas += 1
                if tentativas < 3:
                    print(f"  ⏳ Tropeço na API. A respirar 5s...")
                    time.sleep(5)
                else:
                    print(f"  ❌ Erro definitivo ao puxar {nome}: {e}")
                    
        # Salva no banco em pequenos lotes e limpa a memória para não sobrecarregar
        if len(lista_atualizacao) >= 100:
            for lote in dividir_em_lotes(lista_atualizacao, 100):
                supabase.table("estatisticas_temporada").upsert(lote).execute()
            lista_atualizacao = []

    # Salva os últimos registros residuais que sobraram na lista
    if lista_atualizacao:
        for lote in dividir_em_lotes(lista_atualizacao, 100):
            supabase.table("estatisticas_temporada").upsert(lote).execute()
            
    print("✅ Resgate histórico finalizado com sucesso!")

if __name__ == '__main__':
    resgatar_bolas_de_3_via_carreira()