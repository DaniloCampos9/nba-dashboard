import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
import pandas as pd
from extrator import extrair_dados_defesa, extrair_dados_times
from transformador import carregar_defesa_supabase, carregar_times_supabase
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import commonallplayers
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams

# Carrega as senhas do arquivo .env ANTES de importar o banco
load_dotenv()

# --- IMPORTS DO EXTRATOR ---
from extrator import (
    buscar_dados_brutos_jogador, 
    buscar_estatisticas_carreira, 
    buscar_estatisticas_avancadas_liga, 
    buscar_estatisticas_hustle_liga, 
    buscar_estatisticas_clutch_liga,
    extrair_dados_defesa
)

# --- IMPORTS DO TRANSFORMADOR ---
from transformador import (
    limpar_dados_jogador, 
    limpar_estatisticas_carreira, 
    limpar_estatisticas_avancadas, 
    limpar_estatisticas_hustle, 
    limpar_estatisticas_clutch,
    criar_perfil_basico_liga,
    carregar_defesa_supabase
)

# --- IMPORTS DO CARREGADOR ---
from carregador import (
    enviar_para_banco, 
    enviar_estatisticas_para_banco, 
    enviar_stats_avancadas, 
    enviar_stats_hustle, 
    enviar_stats_clutch,
    limpar_dados_temporada_atual,
    dividir_em_lotes,
    supabase
)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def obter_ids_jogadores_ativos():
    print("Mapeando todos os jogadores ativos da liga...")
    lista_completa = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_dict()
    id_index = lista_completa['resultSets'][0]['headers'].index("PERSON_ID")
    ids = [linha[id_index] for linha in lista_completa['resultSets'][0]['rowSet']]
    print(f"Total de {len(ids)} jogadores encontrados.\n")
    return ids

# =======================================================
# ROTINA 0: CARGA CADASTRAL DE JOGADORES HISTÓRICOS
# =======================================================
def carregar_jogadores_historicos_banco():
    """Busca lendas e jogadores inativos (Kobe, Bird, etc) e salva no Supabase."""
    print("--- INICIANDO CARGA CADASTRAL DE JOGADORES HISTÓRICOS ---")
    try:
        df_completo = commonallplayers.CommonAllPlayers(is_only_current_season=0).get_data_frames()[0]
        
        jogadores_cadastro = []
        for _, row in df_completo.iterrows():
            jogadores_cadastro.append({
                "id": int(row['PERSON_ID']),
                "nome_completo": row['DISPLAY_FIRST_LAST']
                # Não preenchemos time_atual_id pois muitos estão aposentados
            })
        
        if jogadores_cadastro:
            print(f"Salvando {len(jogadores_cadastro)} jogadores no banco...")
            for lote in dividir_em_lotes(jogadores_cadastro, 100):
                supabase.table("jogadores").upsert(lote).execute()
            print("✅ Jogadores históricos carregados com sucesso no Supabase!")
    except Exception as e:
        print(f"Erro ao carregar jogadores históricos: {e}")

# =======================================================
# ROTINA 1: ATUALIZAÇÃO DIÁRIA
# =======================================================
def executar_atualizacao_diaria(temporada_atual="2026-27"):
    """Rotina ultrarrápida otimizada para rodar diariamente no PC."""
    print(f"--- INICIANDO ATUALIZAÇÃO DIÁRIA DA NBA ({temporada_atual}) ---")
    
    ids_jogadores = obter_ids_jogadores_ativos()
    limpar_dados_temporada_atual(temporada_atual)
    
    try:
        print("Baixando Estatísticas Tradicionais (Incluindo 3 Pontos)...")
        tipo = "Regular Season"
        df_trad = leaguedashplayerstats.LeagueDashPlayerStats(season=temporada_atual, season_type_all_star=tipo).get_data_frames()[0]
        
        lista_trad = []
        for _, row in df_trad.iterrows():
            if row['PLAYER_ID'] in ids_jogadores:
                lista_trad.append({
                    "jogador_id": int(row['PLAYER_ID']),
                    "temporada": temporada_atual,
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
        
        if lista_trad: enviar_estatisticas_para_banco(lista_trad)
        
        bruto_adv, _ = buscar_estatisticas_avancadas_liga(temporada_atual)
        perfil_basico = criar_perfil_basico_liga(bruto_adv, temporada_atual)
        if perfil_basico: enviar_para_banco(perfil_basico)

        limpa_adv = limpar_estatisticas_avancadas(bruto_adv, temporada_atual)
        filtrada_adv = [s for s in limpa_adv if s["jogador_id"] in ids_jogadores]
        
        bruto_hustle, _ = buscar_estatisticas_hustle_liga(temporada_atual)
        limpa_hustle = limpar_estatisticas_hustle(bruto_hustle, temporada_atual)
        filtrada_hustle = [s for s in limpa_hustle if s["jogador_id"] in ids_jogadores]
        
        bruto_clutch, _ = buscar_estatisticas_clutch_liga(temporada_atual)
        limpa_clutch = limpar_estatisticas_clutch(bruto_clutch, temporada_atual)
        filtrada_clutch = [s for s in limpa_clutch if s["jogador_id"] in ids_jogadores]
        
        print(f"\n[CARGA] Enviando métricas atualizadas de {temporada_atual}...")
        if filtrada_adv: enviar_stats_avancadas(filtrada_adv)
        if filtrada_hustle: enviar_stats_hustle(filtrada_hustle)
        if filtrada_clutch: enviar_stats_clutch(filtrada_clutch)
        
        df_defesa = extrair_dados_defesa(temporada_atual)
        if not df_defesa.empty:
            df_defesa = df_defesa[df_defesa['PLAYER_ID'].isin(ids_jogadores)]
            carregar_defesa_supabase(df_defesa, supabase)
            
        print("\n--- ATUALIZAÇÃO DIÁRIA CONCLUÍDA COM SUCESSO! ---")
    except Exception as e:
        print(f"[ERRO FATAL NA ATUALIZAÇÃO DIÁRIA]: {e}")

# =======================================================
# ROTINA 2: CARGA HISTÓRICA COMPLETA
# =======================================================
def executar_carga_historica(lista_temporadas):
    print(f"--- INICIANDO CARGA HISTÓRICA ({len(lista_temporadas)} temporadas) ---")
    ids_jogadores = obter_ids_jogadores_ativos()
    
    for temporada in lista_temporadas:
        print(f"\n=========================================================")
        print(f" PROCESSANDO TEMPORADA: {temporada}")
        print(f"=========================================================")
        
        limpar_dados_temporada_atual(temporada)
        
        try:
            tipo = "Regular Season"
            df_trad = leaguedashplayerstats.LeagueDashPlayerStats(season=temporada, season_type_all_star=tipo).get_data_frames()[0]
            lista_trad = []
            for _, row in df_trad.iterrows():
                if row['PLAYER_ID'] in ids_jogadores:
                    lista_trad.append({
                        "jogador_id": int(row['PLAYER_ID']),
                        "temporada": temporada,
                        "tipo_temporada": tipo,
                        "time_abrev": row['TEAM_ABBREVIATION'],
                        "idade": int(row['AGE']),
                        "jogos_disputados": int(row['GP']),
                        "minutos_totais": float(row['MIN']), # 👇 Minutos inseridos aqui também
                        "pontos_totais": int(row['PTS']),
                        "assistencias_totais": int(row['AST']),
                        "rebotes_totais": int(row['REB']),
                        "fg3m_totais": int(row['FG3M']),
                        "fg3a_totais": int(row['FG3A'])
                    })
            if lista_trad: enviar_estatisticas_para_banco(lista_trad)

            bruto_adv, _ = buscar_estatisticas_avancadas_liga(temporada)
            perfil_basico = criar_perfil_basico_liga(bruto_adv, temporada)
            if perfil_basico: enviar_para_banco(perfil_basico)

            limpa_adv = limpar_estatisticas_avancadas(bruto_adv, temporada)
            filtrada_adv = [s for s in limpa_adv if s["jogador_id"] in ids_jogadores]
            
            bruto_hustle, _ = buscar_estatisticas_hustle_liga(temporada)
            limpa_hustle = limpar_estatisticas_hustle(bruto_hustle, temporada)
            filtrada_hustle = [s for s in limpa_hustle if s["jogador_id"] in ids_jogadores]
            
            bruto_clutch, _ = buscar_estatisticas_clutch_liga(temporada)
            limpa_clutch = limpar_estatisticas_clutch(bruto_clutch, temporada)
            filtrada_clutch = [s for s in limpa_clutch if s["jogador_id"] in ids_jogadores]
            
            if filtrada_adv: enviar_stats_avancadas(filtrada_adv)
            if filtrada_hustle: enviar_stats_hustle(filtrada_hustle)
            if filtrada_clutch: enviar_stats_clutch(filtrada_clutch)
            
            df_defesa = extrair_dados_defesa(temporada)
            if not df_defesa.empty:
                df_defesa = df_defesa[df_defesa['PLAYER_ID'].isin(ids_jogadores)]
                carregar_defesa_supabase(df_defesa, supabase)
                
        except Exception as e:
            print(f"[ERRO FATAL NA TEMPORADA {temporada}]: {e}")
            
        time.sleep(3)
    print("\n--- CARGA HISTÓRICA CONCLUÍDA COM SUCESSO! ---")

# =======================================================
# ROTINA 3: BACKFILL DE PLAYOFFS
# =======================================================
def executar_backfill_playoffs(lista_temporadas):
    print(f"--- INICIANDO DOWNLOAD COMPLETO DE PLAYOFFS ---")
    tipo = "Playoffs"
    
    for temporada in lista_temporadas:
        print(f"\nBaixando Playoffs da temporada: {temporada}")
        
        df_times = extrair_dados_times(temporada, tipo)
        if not df_times.empty: carregar_times_supabase(df_times, supabase)
        
        df_def = extrair_dados_defesa(temporada, tipo)
        if not df_def.empty: carregar_defesa_supabase(df_def, supabase)
        
        brutos_adv, _ = buscar_estatisticas_avancadas_liga(temporada, tipo)
        lista_adv = limpar_estatisticas_avancadas(brutos_adv, temporada, tipo)
        sucesso_adv = 0
        for d in lista_adv:
            try: 
                supabase.table("stats_avancadas").insert(d).execute()
                sucesso_adv += 1
            except: pass
        print(f"Avançadas: {sucesso_adv} inseridos.")

        try:
            df_trad = leaguedashplayerstats.LeagueDashPlayerStats(season=temporada, season_type_all_star=tipo).get_data_frames()[0]
            lista_trad = []
            for _, row in df_trad.iterrows():
                lista_trad.append({
                    "jogador_id": int(row['PLAYER_ID']),
                    "temporada": temporada,
                    "tipo_temporada": tipo,
                    "time_abrev": row['TEAM_ABBREVIATION'],
                    "idade": int(row['AGE']),
                    "jogos_disputados": int(row['GP']),
                    "minutos_totais": float(row['MIN']), # 👇 Minutos inseridos nos playoffs também
                    "pontos_totais": int(row['PTS']),
                    "assistencias_totais": int(row['AST']),
                    "rebotes_totais": int(row['REB']),
                    "fg3m_totais": int(row['FG3M']),
                    "fg3a_totais": int(row['FG3A'])
                })
            
            if lista_trad:
                enviar_estatisticas_para_banco(lista_trad)
                print(f"Tradicionais: Atualizados com 3 Pontos e Minutos.")
        except Exception as e:
            print(f"Erro Tradicionais: {e}")
            
        time.sleep(3)
        
# =======================================================
# ROTINA 4: ATUALIZAÇÃO DE ELENCOS OFICIAIS (ROSTER)
# =======================================================
def atualizar_elencos_oficiais(temporada="2026-27"):
    print(f"--- BASTIDORES: BUSCANDO ELENCOS OFICIAIS DA TEMPORADA {temporada} ---")
    nba_teams = teams.get_teams()
    atualizacoes_cadastrais = []
    
    for team in nba_teams:
        team_id = team['id']
        nome_time = team['full_name']
        print(f"Puxando elenco: {nome_time}...")
        try:
            roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=temporada).get_data_frames()[0]
            for _, row in roster.iterrows():
                atualizacoes_cadastrais.append({
                    "id": int(row['PLAYER_ID']),
                    "time_atual_id": int(team_id)
                })
            time.sleep(0.6)
        except Exception as e:
            print(f"Erro ao buscar elenco do {nome_time}: {e}")
            
    if atualizacoes_cadastrais:
        print(f"\nSalvando {len(atualizacoes_cadastrais)} jogadores em suas respectivas franquias...")
        for lote in dividir_em_lotes(atualizacoes_cadastrais, 100):
            supabase.table("jogadores").upsert(lote).execute()
        print("✅ ELENCOS ATUALIZADOS COM SUCESSO ABSOLUTO!")

if __name__ == "__main__":
    # =========================================================================
    # PAINEL DE CONTROLE - DESCOMENTE A ROTINA QUE VOCÊ QUER RODAR HOJE
    # =========================================================================
    
    # 1. PARA PUXAR KOBE, BIRD E A HISTÓRIA (Rode apenas 1 vez)
    #carregar_jogadores_historicos_banco()
    
    # 2. PARA ATUALIZAR O ELENCO DAS EQUIPES
    #atualizar_elencos_oficiais("2026-27")
    
    # 3. ATUALIZAÇÃO DIÁRIA NORMAL
    executar_atualizacao_diaria("2026-27")