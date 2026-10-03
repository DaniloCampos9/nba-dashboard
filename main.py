import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from extrator import extrair_dados_defesa, extrair_dados_times
from transformador import carregar_defesa_supabase, carregar_times_supabase
from nba_api.stats.endpoints import leaguedashplayerstats

# Carrega as senhas do arquivo .env ANTES de importar o banco
load_dotenv()

from nba_api.stats.endpoints import commonallplayers

# --- IMPORTS DO EXTRATOR ---
from extrator import (
    buscar_dados_brutos_jogador, 
    buscar_estatisticas_carreira, 
    buscar_estatisticas_avancadas_liga, 
    buscar_estatisticas_hustle_liga, 
    buscar_estatisticas_clutch_liga,
    extrair_dados_defesa  # Nossa nova função!
)

# --- IMPORTS DO TRANSFORMADOR ---
from transformador import (
    limpar_dados_jogador, 
    limpar_estatisticas_carreira, 
    limpar_estatisticas_avancadas, 
    limpar_estatisticas_hustle, 
    limpar_estatisticas_clutch,
    criar_perfil_basico_liga,
    carregar_defesa_supabase  # Nossa nova função!
)

# --- IMPORTS DO CARREGADOR ---
from carregador import (
    enviar_para_banco, 
    enviar_estatisticas_para_banco, 
    enviar_stats_avancadas, 
    enviar_stats_hustle, 
    enviar_stats_clutch,
    limpar_dados_temporada_atual,
    supabase # Puxando a conexão do banco para enviar pra função de defesa
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
# ROTINA 1: ATUALIZAÇÃO DIÁRIA (A QUE VAMOS DEIXAR LIGADA)
# =======================================================
def executar_atualizacao_diaria(temporada_atual="2026-27"):
    """Rotina ultrarrápida otimizada para rodar diariamente no PC."""
    print(f"--- INICIANDO ATUALIZAÇÃO DIÁRIA DA NBA ({temporada_atual}) ---")
    
    ids_jogadores = obter_ids_jogadores_ativos()
    limpar_dados_temporada_atual(temporada_atual)
    
    try:
        bruto_adv, _ = buscar_estatisticas_avancadas_liga(temporada_atual)
        
        perfil_basico = criar_perfil_basico_liga(bruto_adv, temporada_atual)
        if perfil_basico: 
            enviar_para_banco(perfil_basico)

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
        
        # 👉 Defesa incluída na rotina diária
        df_defesa = extrair_dados_defesa(temporada_atual)
        if not df_defesa.empty:
            df_defesa = df_defesa[df_defesa['PLAYER_ID'].isin(ids_jogadores)]
            carregar_defesa_supabase(df_defesa, supabase)
            
        print("\n--- ATUALIZAÇÃO DIÁRIA CONCLUÍDA COM SUCESSO! ---")
        
    except Exception as e:
        print(f"[ERRO FATAL NA ATUALIZAÇÃO DIÁRIA]: {e}")


# =======================================================
# ROTINA 2: CARGA HISTÓRICA COMPLETA (GUARDADA PARA USO FUTURO)
# =======================================================
def executar_carga_historica(lista_temporadas):
    """Loop que roda o ETL completo para todas as temporadas passadas."""
    print(f"--- INICIANDO CARGA HISTÓRICA ({len(lista_temporadas)} temporadas) ---")
    ids_jogadores = obter_ids_jogadores_ativos()
    
    for temporada in lista_temporadas:
        print(f"\n=========================================================")
        print(f" PROCESSANDO TEMPORADA: {temporada}")
        print(f"=========================================================")
        
        limpar_dados_temporada_atual(temporada)
        
        try:
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
# ROTINA 3: CARGA APENAS DE DEFESA (GUARDADA PARA USO FUTURO)
# =======================================================
def executar_carga_apenas_defesa(lista_temporadas):
    """Loop focado APENAS em puxar os dados de Defesa."""
    print(f"--- INICIANDO CARGA EXCLUSIVA DE DEFESA ({len(lista_temporadas)} temporadas) ---")
    ids_jogadores = obter_ids_jogadores_ativos()
    
    for temporada in lista_temporadas:
        try:
            df_defesa = extrair_dados_defesa(temporada)
            if not df_defesa.empty:
                df_defesa = df_defesa[df_defesa['PLAYER_ID'].isin(ids_jogadores)]
                carregar_defesa_supabase(df_defesa, supabase)
        except Exception as e:
            print(f"[ERRO NA TEMPORADA {temporada}]: {e}")
        time.sleep(3)

def executar_carga_apenas_times(lista_temporadas):
    """Loop focado APENAS em puxar os dados dos Times."""
    print(f"--- INICIANDO CARGA EXCLUSIVA DE TIMES ({len(lista_temporadas)} temporadas) ---")
    
    for temporada in lista_temporadas:
        print(f"\n=========================================================")
        print(f" PUXANDO TIMES: {temporada}")
        print(f"=========================================================")
        
        try:
            df_times = extrair_dados_times(temporada)
            if not df_times.empty:
                carregar_times_supabase(df_times, supabase)
            else:
                print("Nenhum dado de time retornado.")
                
        except Exception as e:
            print(f"[ERRO NA TEMPORADA {temporada}]: {e}")
            
        time.sleep(3)
        
    print("\n--- CARGA DE TIMES CONCLUÍDA COM SUCESSO! ---")
# Certifique-se de que os imports no topo do main.py estejam ok.
def executar_backfill_playoffs(lista_temporadas):
    """Loop focado em puxar todas as tabelas dos Playoffs antigos."""
    print(f"--- INICIANDO DOWNLOAD COMPLETO DE PLAYOFFS ---")
    tipo = "Playoffs"
    
    for temporada in lista_temporadas:
        print(f"\nBaixando Playoffs da temporada: {temporada}")
        
        # 1. Times
        df_times = extrair_dados_times(temporada, tipo)
        if not df_times.empty: carregar_times_supabase(df_times, supabase)
        
        # 2. Defesa 
        df_def = extrair_dados_defesa(temporada, tipo)
        if not df_def.empty: carregar_defesa_supabase(df_def, supabase)
        
        # 3. Avançadas (Jogadores)
        brutos_adv, _ = buscar_estatisticas_avancadas_liga(temporada, tipo)
        lista_adv = limpar_estatisticas_avancadas(brutos_adv, temporada, tipo)
        sucesso_adv = 0
        for d in lista_adv:
            try: 
                supabase.table("stats_avancadas").insert(d).execute()
                sucesso_adv += 1
            except: pass
        print(f"Avançadas: {sucesso_adv} inseridos.")

        # 4. Tradicionais (Atalho: Puxa da liga inteira de uma vez)
        try:
            df_trad = leaguedashplayerstats.LeagueDashPlayerStats(season=temporada, season_type_all_star=tipo).get_data_frames()[0]
            sucesso_trad = 0
            for _, row in df_trad.iterrows():
                dados = {
                    "jogador_id": int(row['PLAYER_ID']),
                    "temporada": temporada,
                    "tipo_temporada": tipo,
                    "time_abrev": row['TEAM_ABBREVIATION'],
                    "idade": int(row['AGE']),
                    "jogos_disputados": int(row['GP']),
                    "pontos_totais": int(row['PTS']),
                    "assistencias_totais": int(row['AST']),
                    "rebotes_totais": int(row['REB'])
                }
                try:
                    supabase.table("estatisticas_temporada").insert(dados).execute()
                    sucesso_trad += 1
                except: pass
            print(f"Tradicionais: {sucesso_trad} inseridos.")
        except Exception as e:
            print(f"Erro Tradicionais: {e}")
            
        time.sleep(3) # Pausa dramática para a API não nos bloquear

if __name__ == "__main__":
    temporadas = ["2026-27", "2025-26", "2024-25", "2023-24", "2022-23"]
    # Comente a sua carga antiga e rode apenas essa para baixar os Playoffs!
    executar_backfill_playoffs(temporadas)