import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re


def criar_pasta_imagens(caminho_pasta):
    """Cria a pasta IMAGES se ela não existir"""
    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)
        print(f"Pasta criada: {caminho_pasta}")
    else:
        print(f"Pasta já existe: {caminho_pasta}")


def limpar_nome_arquivo(nome):
    """Remove caracteres inválidos do nome do arquivo"""
    # Remove ou substitui caracteres que não são válidos em nomes de arquivo
    nome_limpo = re.sub(r'[<>:"/\\|?*]', '_', nome)
    nome_limpo = re.sub(r'\s+', '_', nome_limpo)  # Substitui espaços por underscore
    return nome_limpo


def extrair_imagem_principal(url):
    """Extrai a URL da imagem principal de uma página do LOTR wiki"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        print(f"    Acessando URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Lista de métodos para encontrar imagens, em ordem de prioridade
        imagem_url = None
        metodo_usado = ""

        # Método 1: Infobox principal (portable-infobox)
        if not imagem_url:
            infobox = soup.find('aside', class_='portable-infobox')
            if infobox:
                img_tag = infobox.find('img')
                if img_tag and img_tag.get('src'):
                    imagem_url = img_tag['src']
                    metodo_usado = "infobox portable"

        # Método 2: Infobox alternativa (pi-item pi-image)
        if not imagem_url:
            figure = soup.find('figure', class_='pi-item pi-image')
            if figure:
                img_tag = figure.find('img')
                if img_tag and img_tag.get('src'):
                    imagem_url = img_tag['src']
                    metodo_usado = "figure pi-item"

        # Método 3: Infobox clássica (infobox)
        if not imagem_url:
            infobox_classic = soup.find('table', class_='infobox')
            if infobox_classic:
                img_tag = infobox_classic.find('img')
                if img_tag and img_tag.get('src'):
                    imagem_url = img_tag['src']
                    metodo_usado = "infobox clássica"

        # Método 4: Primeira imagem do artigo (thumbinner)
        if not imagem_url:
            thumb = soup.find('div', class_='thumbinner')
            if thumb:
                img_tag = thumb.find('img')
                if img_tag and img_tag.get('src'):
                    imagem_url = img_tag['src']
                    metodo_usado = "thumbinner"

        # Método 5: Galeria de imagens
        if not imagem_url:
            gallery = soup.find('ul', class_='gallery')
            if gallery:
                img_tag = gallery.find('img')
                if img_tag and img_tag.get('src'):
                    imagem_url = img_tag['src']
                    metodo_usado = "galeria"

        # Método 6: Qualquer imagem no conteúdo principal (mais específico)
        if not imagem_url:
            content_div = soup.find('div', class_='mw-parser-output')
            if content_div:
                # Procura por imagens em divs de imagem específicos
                for img_container in content_div.find_all(['div', 'figure'], class_=lambda x: x and any(
                        cls in x for cls in ['image', 'thumb', 'floatright', 'floatleft'])):
                    img_tag = img_container.find('img')
                    if img_tag and img_tag.get('src'):
                        src = img_tag['src']
                        if is_valid_image(src):
                            imagem_url = src
                            metodo_usado = "container de imagem"
                            break

        # Método 7: Primeira imagem válida no conteúdo
        if not imagem_url:
            content_div = soup.find('div', class_='mw-parser-output')
            if content_div:
                imgs = content_div.find_all('img')
                for img in imgs:
                    src = img.get('src', '')
                    if is_valid_image(src):
                        imagem_url = src
                        metodo_usado = "primeira imagem válida"
                        break

        # Método 8: Busca global por qualquer imagem válida
        if not imagem_url:
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                src = img.get('src', '')
                if is_valid_image(src):
                    imagem_url = src
                    metodo_usado = "busca global"
                    break

        if imagem_url:
            # Garante que a URL está completa
            if imagem_url.startswith('//'):
                imagem_url = 'https:' + imagem_url
            elif not imagem_url.startswith('http'):
                imagem_url = urljoin(url, imagem_url)

            # Remove parâmetros de redimensionamento para obter imagem original
            imagem_url = get_original_image_url(imagem_url)

            print(f"    ✓ Imagem encontrada via {metodo_usado}: {imagem_url}")
            return imagem_url
        else:
            print(f"    ✗ Nenhuma imagem encontrada após todos os métodos")

        return None

    except Exception as e:
        print(f"    ✗ Erro ao processar {url}: {e}")
        return None


def is_valid_image(src):
    """Verifica se a URL da imagem é válida e não é um ícone/logo"""
    if not src:
        return False

    # URLs que devemos evitar
    avoid_keywords = [
        'icon', 'edit', 'commons-logo', 'wikia-logo', 'discord',
        'facebook', 'twitter', 'youtube', 'favicon', 'arrow',
        'loading', 'spinner', 'thumbnail', '/ui/', 'button'
    ]

    src_lower = src.lower()

    # Evita URLs com palavras-chave problemáticas
    if any(keyword in src_lower for keyword in avoid_keywords):
        return False

    # Deve conter domínios de imagem válidos
    valid_domains = ['static.wikia.nocookie.net', 'vignette.wikia.nocookie.net', 'images.wikia.com']
    if any(domain in src for domain in valid_domains):
        return True

    # Ou ter extensões de imagem válidas
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if any(ext in src_lower for ext in valid_extensions):
        return True

    return False


def get_original_image_url(url):
    """Converte URL de imagem redimensionada para versão original"""
    # Remove parâmetros de redimensionamento
    if '/revision/latest/scale-to-width-down/' in url:
        url = url.split('/revision/latest/scale-to-width-down/')[0] + '/revision/latest'
    elif '/revision/latest/scale-to-width/' in url:
        url = url.split('/revision/latest/scale-to-width/')[0] + '/revision/latest'
    elif '/revision/latest/top-crop/width/' in url:
        url = url.split('/revision/latest/top-crop/width/')[0] + '/revision/latest'
    elif '/revision/latest/thumbnail/width/' in url:
        url = url.split('/revision/latest/thumbnail/width/')[0] + '/revision/latest'

    return url


def baixar_imagem(url_imagem, caminho_arquivo):
    """Baixa uma imagem da URL e salva no caminho especificado"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url_imagem, headers=headers, timeout=15)
        response.raise_for_status()

        with open(caminho_arquivo, 'wb') as f:
            f.write(response.content)

        return True

    except Exception as e:
        print(f"Erro ao baixar imagem {url_imagem}: {e}")
        return False


def processar_personagens(arquivo_csv, pasta_destino):
    """Função principal que processa o CSV e baixa as imagens"""

    # Lê o arquivo CSV
    try:
        df = pd.read_csv(arquivo_csv)
        print(f"Arquivo CSV carregado com {len(df)} personagens")

        # Mostra as colunas disponíveis e algumas linhas de exemplo
        print(f"Colunas disponíveis: {list(df.columns)}")
        print("\n=== PRIMEIRAS 3 LINHAS DO CSV (para debug) ===")
        for i in range(min(3, len(df))):
            print(f"Linha {i + 1}:")
            print(f"  character_from_quotes: {df.iloc[i]['character_from_quotes']}")
            print(f"  matched_name_in_characters: {df.iloc[i]['matched_name_in_characters']}")
            print(f"  wiki_url: {df.iloc[i]['wiki_url']}")
        print("=" * 50)

    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return

    # Cria a pasta de destino
    criar_pasta_imagens(pasta_destino)

    sucessos = 0
    falhas = 0
    personagens_falharam = []  # Lista para armazenar personagens que falharam

    # Processa cada linha do CSV
    for index, row in df.iterrows():
        try:
            # Usa os nomes corretos das colunas do CSV
            nome_personagem = str(row['matched_name_in_characters']) if pd.notna(
                row['matched_name_in_characters']) else str(row['character_from_quotes'])
            link_wiki = str(row['wiki_url'])

            # Verifica se os dados são válidos
            if pd.isna(row['wiki_url']) or link_wiki.lower() in ['nan', 'none', '']:
                print(f"Linha {index + 1}: Link do wiki não disponível para {nome_personagem}")
                falhas += 1
                personagens_falharam.append(f"{nome_personagem} - Link não disponível")
                continue

            print(f"\nProcessando: {nome_personagem}")
            print(f"URL: {link_wiki}")

            # Extrai a URL da imagem principal
            url_imagem = extrair_imagem_principal(link_wiki)

            if url_imagem:
                print(f"Imagem encontrada: {url_imagem}")

                # Determina a extensão do arquivo
                parsed_url = urlparse(url_imagem)
                extensao = os.path.splitext(parsed_url.path)[1]
                if not extensao:
                    extensao = '.jpg'  # extensão padrão

                # Cria o nome do arquivo
                nome_arquivo = limpar_nome_arquivo(nome_personagem) + extensao
                caminho_completo = os.path.join(pasta_destino, nome_arquivo)

                # Baixa a imagem
                if baixar_imagem(url_imagem, caminho_completo):
                    print(f"✓ Imagem salva: {nome_arquivo}")
                    sucessos += 1
                else:
                    print(f"✗ Falha ao baixar imagem de {nome_personagem}")
                    falhas += 1
                    personagens_falharam.append(f"{nome_personagem} - Falha ao baixar imagem")
            else:
                print(f"✗ Nenhuma imagem encontrada para {nome_personagem}")
                falhas += 1
                personagens_falharam.append(f"{nome_personagem} - Nenhuma imagem encontrada")

            # Pausa entre requisições para não sobrecarregar o servidor
            time.sleep(2)

        except Exception as e:
            print(f"Erro ao processar linha {index + 1}: {e}")
            falhas += 1
            personagens_falharam.append(f"{nome_personagem} - Erro: {str(e)}")

    print(f"\n=== RESUMO ===")
    print(f"Total de personagens processados: {len(df)}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {falhas}")

    # Mostra quais personagens falharam
    if personagens_falharam:
        print(f"\n=== PERSONAGENS QUE FALHARAM ({len(personagens_falharam)}) ===")
        for i, personagem in enumerate(personagens_falharam, 1):
            print(f"{i}. {personagem}")
    else:
        print(f"\n🎉 Todas as imagens foram baixadas com sucesso!")


# Configuração principal
if __name__ == "__main__":
    # Caminhos
    arquivo_csv = "characters_with_links.csv"  # Nome do seu arquivo CSV
    pasta_destino = r"C:\Users\User\Desktop\Lord Of Rings Website\IMAGES"

    print("=== SCRIPT DE DOWNLOAD DE IMAGENS DOS PERSONAGENS LOTR ===")
    print(f"Arquivo CSV: {arquivo_csv}")
    print(f"Pasta de destino: {pasta_destino}")

    # Verifica se o arquivo CSV existe
    if not os.path.exists(arquivo_csv):
        print(f"ERRO: Arquivo {arquivo_csv} não encontrado!")
        print("Certifique-se de que o arquivo está na mesma pasta do script.")
    else:
        processar_personagens(arquivo_csv, pasta_destino)

    input("\nPressione Enter para sair...")
