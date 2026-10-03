import urllib.request
import xml.etree.ElementTree as ET

def obter_noticias_jogador(nome_jogador):
    """Busca as últimas notícias do jogador na web usando RSS público do Google News."""
    try:
        query = nome_jogador.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}+NBA&hl=en-US&gl=US&ceid=US:en"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        noticias = []
        
        # Coleta até 4 notícias mais recentes
        for item in root.findall('./channel/item')[:4]:
            titulo = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else "#"
            data = item.find('pubDate').text if item.find('pubDate') is not None else ""
            
            # Formata a data para ficar mais limpa (ex: Sat, 03 Oct 2026)
            data_limpa = data[:16] if len(data) >= 16 else data
            
            noticias.append({
                "titulo": titulo,
                "link": link,
                "data": data_limpa
            })
            
        return noticias
    except Exception:
        return []