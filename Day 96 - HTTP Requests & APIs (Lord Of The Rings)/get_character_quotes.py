import requests
import json
import os

API_URL = "https://the-one-api.dev/v2"
ACCESS_TOKEN = ""

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def get_character_quotes(character_id):
    try:
        response = requests.get(f"{API_URL}/character/{character_id}/quote", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar frases para o personagem {character_id}: {e}")
        return {"docs": []}

if __name__ == "__main__":
    with open("characters.json", "r", encoding="utf-8") as f:
        characters_data = json.load(f)

    all_quotes = {}
    for character in characters_data["docs"]:
        character_id = character["_id"]
        character_name = character["name"]
        print(f"Buscando frases para {character_name} ({character_id})...")
        quotes_data = get_character_quotes(character_id)
        if quotes_data and quotes_data["docs"]:
            all_quotes[character_id] = [q["dialog"] for q in quotes_data["docs"]]

    with open("character_quotes.json", "w", encoding="utf-8") as f:
        json.dump(all_quotes, f, ensure_ascii=False, indent=4)
    print("Frases dos personagens salvas em character_quotes.json")


