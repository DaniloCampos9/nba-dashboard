import os

# Pastas e arquivos que não precisamos mandar para a IA
IGNORAR_PASTAS = ['.git', '__pycache__', 'venv', '.venv', 'env']
IGNORAR_ARQUIVOS = ['gerar_contexto.py', 'patch_3_pontos.py']

def gerar_arquivo_contexto(nome_saida='contexto_nba.txt'):
    print("Empacotando projeto...")
    
    with open(nome_saida, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk('.'):
            # Filtra as pastas para o script não entrar nos ambientes virtuais
            dirs[:] = [d for d in dirs if d not in IGNORAR_PASTAS]

            for file in files:
                if file.endswith('.py') and file not in IGNORAR_ARQUIVOS:
                    caminho_completo = os.path.join(root, file)
                    
                    # Cria um cabeçalho bonitinho para a IA saber qual arquivo está lendo
                    outfile.write(f"\n{'='*80}\n")
                    outfile.write(f"ARQUIVO: {caminho_completo}\n")
                    outfile.write(f"{'='*80}\n\n")
                    
                    try:
                        with open(caminho_completo, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                            outfile.write("\n")
                    except Exception as e:
                        outfile.write(f"# Erro ao ler arquivo: {e}\n")
                        
    print(f"✅ Tudo pronto! Contexto consolidado no arquivo: {nome_saida}")

if __name__ == '__main__':
    gerar_arquivo_contexto()