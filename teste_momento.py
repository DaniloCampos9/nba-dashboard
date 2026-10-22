from extrator import buscar_estatisticas_clutch_liga
from transformador import limpar_estatisticas_clutch
from carregador import enviar_stats_clutch

print("Baixando dados de Clutch da NBA (2026-27)...")
bruto_clutch, temporada = buscar_estatisticas_clutch_liga("2026-27", "Regular Season")
lista_clutch = limpar_estatisticas_clutch(bruto_clutch, temporada, "Regular Season")

print(f"Itens de clutch obtidos: {len(lista_clutch)}")
if lista_clutch:
    enviar_stats_clutch(lista_clutch)
    print("✅ Dados de Clutch enviados com sucesso para o Supabase!")
else:
    print("❌ Nenhum dado retornado.")