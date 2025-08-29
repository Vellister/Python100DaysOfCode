# build_quotes_csv.py
import os
import csv
import time
import random
import requests
from collections import defaultdict
from dotenv import load_dotenv

# --- Config ---
API_BASE = "https://the-one-api.dev/v2"
PAGE_LIMIT = 1000
NUM_CHARACTERS = 60
SLEEP_BETWEEN_CALLS = 0.2

def get_headers():
    load_dotenv()
    token = os.getenv("ONE_API_KEY")
    if not token:
        raise RuntimeError(
            "ONE_API_KEY não encontrado no .env. "
            "Crie um arquivo .env com a linha: ONE_API_KEY=seu_token"
        )
    return {"Authorization": f"Bearer {token}"}

def paginate(endpoint, params=None, headers=None):
    """Itera por todas as páginas de um endpoint da The One API."""
    if params is None:
        params = {}
    page = 1
    while True:
        merged = dict(params)
        merged.setdefault("limit", PAGE_LIMIT)
        merged["page"] = page
        url = f"{API_BASE}{endpoint}"
        resp = requests.get(url, headers=headers, params=merged, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Erro {resp.status_code} ao chamar {url}: {resp.text}")
        data = resp.json()
        docs = data.get("docs", [])
        total = data.get("total")
        pages = data.get("pages")
        yield from docs


        if pages is not None:
            if page >= pages:
                break
        else:
            # fallback se a API não mandar 'pages'
            if len(docs) < merged["limit"]:
                break

        page += 1
        time.sleep(SLEEP_BETWEEN_CALLS)

def fetch_all_quotes(headers):
    quotes_by_char = defaultdict(list)
    for q in paginate("/quote", headers=headers):
        dialog = q.get("dialog")
        char_id = q.get("character")
        if dialog and char_id:
            quotes_by_char[char_id].append(dialog.strip())
    return quotes_by_char

def fetch_all_characters(headers):
    id_to_name = {}
    for c in paginate("/character", headers=headers):
        _id = c.get("_id")
        name = c.get("name")
        if _id and name:
            id_to_name[_id] = name
    return id_to_name

def main():
    headers = get_headers()
    print("Baixando todas as quotes (com paginação)...")
    quotes_by_char = fetch_all_quotes(headers)
    print(f" Quotes coletadas para {len(quotes_by_char)} personagens.")

    print(" Baixando todos os personagens...")
    id_to_name = fetch_all_characters(headers)
    print(f" Personagens carregados: {len(id_to_name)}")

    # Ordena personagens por quantidade de frases (desc) para garantir que teremos 60 com frase
    char_ids_sorted = sorted(
        quotes_by_char.keys(),
        key=lambda cid: len(quotes_by_char[cid]),
        reverse=True
    )

    rows = []
    for cid in char_ids_sorted:
        if len(rows) >= NUM_CHARACTERS:
            break
        name = id_to_name.get(cid)
        if not name:
            continue
        qlist = quotes_by_char[cid]
        if not qlist:
            continue
        quote = random.choice(qlist)
        rows.append({"character": name, "quote": quote})

    if not rows:
        raise RuntimeError(
            "Nenhuma linha gerada. Verifique sua chave (ONE_API_KEY) e tente novamente."
        )

    out_path = "quotes.csv"
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["character", "quote"])
        writer.writeheader()
        writer.writerows(rows)

    print(f" Gerado {out_path} com {len(rows)} personagens (cada um com 1 frase).")

if __name__ == "__main__":
    main()
