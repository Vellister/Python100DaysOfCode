import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

URL = "https://pokemondb.net/pokedex/all"


def get_pokemon_types():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table#pokedex tbody tr")

    type_counts = {}
    seen_pokemon = set()

    for row in rows:
        name = row.select_one("a.ent-name").get_text(strip=True)
        if name in seen_pokemon:
            continue
        seen_pokemon.add(name)

        types = [t.get_text(strip=True) for t in row.select("a.type-icon")]
        for t in types:
            t_norm = t.strip().capitalize()
            type_counts[t_norm] = type_counts.get(t_norm, 0) + 1

    return type_counts


def plot_pie(data):
    df = pd.DataFrame.from_dict(data, orient="index", columns=["Count"])
    df = df.sort_values(by="Count", ascending=False)
    df.to_csv("pokemon_type_counts.csv")

    plt.figure(figsize=(10, 10))
    plt.pie(df["Count"], labels=df.index, autopct='%1.1f%%', startangle=140)
    plt.title("Distribuição de Pokémons por Tipo")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("pokemon_type_distribution.png")
    plt.show()


if __name__ == "__main__":
    type_counts = get_pokemon_types()
    plot_pie(type_counts)
    print("success!!")
