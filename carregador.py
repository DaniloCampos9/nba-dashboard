import os
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_fixed

URL = "https://qqtvqrlrcgctngghwvfd.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHZxcmxyY2djdG5nZ2h3dmZkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDYyMzAyMywiZXhwIjoyMTA2MTk5MDIzfQ.7BRJMTOpv4aSAHwo-iPzdQHE7Yd1bpyXfZPMHoMmUF0"


supabase: Client = create_client(URL, KEY)

def dividir_em_lotes(lista, tamanho=100):
    """Fatia listas gigantes em pedaços menores para o banco de dados não engasgar."""
    for i in range(0, len(lista), tamanho):
        yield lista[i:i + tamanho]

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def enviar_para_banco(dados_limpos):
    if not dados_limpos: return
    print(f"Enviando {len(dados_limpos)} perfis em lotes de 100...")
    for lote in dividir_em_lotes(dados_limpos, 100):
        supabase.table("jogadores").upsert(lote).execute()
    print("Sucesso! Perfis carregados.")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def enviar_estatisticas_para_banco(lista_temporadas):
    if not lista_temporadas: return
    print(f"Enviando {len(lista_temporadas)} stats tradicionais em lotes de 100...")
    for lote in dividir_em_lotes(lista_temporadas, 100):
        supabase.table("estatisticas_temporada").upsert(lote).execute()
    print("Sucesso! Tradicionais carregadas.")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def enviar_stats_avancadas(lista_stats):
    if not lista_stats: return
    print(f"Enviando {len(lista_stats)} stats avançadas em lotes de 100...")
    for lote in dividir_em_lotes(lista_stats, 100):
        supabase.table("stats_avancadas").upsert(lote).execute()
    print("Sucesso! Avançadas carregadas.")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def enviar_stats_hustle(lista_stats):
    if not lista_stats: return
    print(f"Enviando {len(lista_stats)} stats de hustle em lotes de 100...")
    for lote in dividir_em_lotes(lista_stats, 100):
        supabase.table("stats_hustle").upsert(lote).execute()
    print("Sucesso! Hustle carregado.")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def enviar_stats_clutch(lista_stats):
    if not lista_stats: return
    print(f"Enviando {len(lista_stats)} stats clutch em lotes de 100...")
    for lote in dividir_em_lotes(lista_stats, 100):
        supabase.table("stats_clutch").upsert(lote).execute()
    print("Sucesso! Clutch carregado.")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def limpar_dados_temporada_atual(temporada):
    """Apaga os dados da temporada atual para evitar duplicidade na carga diária otimizada."""
    print(f"Limpando registros antigos da temporada {temporada} no banco...")
    supabase.table("stats_avancadas").delete().eq("temporada", temporada).execute()
    supabase.table("stats_hustle").delete().eq("temporada", temporada).execute()
    supabase.table("stats_clutch").delete().eq("temporada", temporada).execute()
    print("Limpeza concluída! Banco pronto para os dados novos.")