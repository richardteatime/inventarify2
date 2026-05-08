#!/usr/bin/env python3
"""
Seed dati demo per Inventarify.
Cancella dati esistenti e inserisce prodotti, menu, vendite e ordini di esempio.

Uso:
    export APPWRITE_ENDPOINT=https://appwrite.app.easlydev.online/v1
    export APPWRITE_PROJECT=xxxxxxxx
    export APPWRITE_API_KEY=xxxxxxxx
    python scripts/seed-demo.py
"""

import os
import sys
import random
from datetime import datetime, timedelta
import requests

ENDPOINT = os.environ.get("APPWRITE_ENDPOINT", "").rstrip("/")
PROJECT = os.environ.get("APPWRITE_PROJECT", "")
API_KEY = os.environ.get("APPWRITE_API_KEY", "")
DB_ID = "inventarify"

if not ENDPOINT or not PROJECT or not API_KEY:
    print("❌ Imposta APPWRITE_ENDPOINT, APPWRITE_PROJECT e APPWRITE_API_KEY")
    sys.exit(1)

HEADERS = {
    "X-Appwrite-Project": PROJECT,
    "X-Appwrite-Key": API_KEY,
    "Content-Type": "application/json",
}

PERMISSIONS = ['read("users")', 'update("users")', 'delete("users")']

PRODOTTI = [
    ("Pasta Spaghetti", 25, "kg", 5),
    ("Pasta Penne", 20, "kg", 5),
    ("Riso Carnaroli", 15, "kg", 3),
    ("Pomodori Pelati", 30, "lattine", 8),
    ("Passata di Pomodoro", 12, "litri", 3),
    ("Olio Extravergine", 18, "litri", 4),
    ("Parmigiano Reggiano", 8, "kg", 2),
    ("Pecorino Romano", 6, "kg", 1.5),
    ("Guanciale", 4, "kg", 1),
    ("Pancetta", 5, "kg", 1.5),
    ("Uova", 120, "pz", 24),
    ("Pepe Nero", 2, "kg", 0.5),
    ("Sale Marino", 5, "kg", 1),
    ("Aglio", 3, "kg", 0.5),
    ("Basilico Fresco", 1.5, "kg", 0.3),
    ("Mozzarella Fior di Latte", 12, "kg", 3),
    ("Bufala Campana", 8, "kg", 2),
    ("Prosciutto Crudo", 5, "kg", 1.5),
    ("Funghi Porcini", 3, "kg", 0.5),
    ("Vino Rosso Chianti", 24, "bottiglie", 6),
    ("Vino Bianco Vernaccia", 18, "bottiglie", 4),
    ("Acqua Naturale", 60, "bottiglie", 12),
    ("Acqua Frizzante", 40, "bottiglie", 10),
    ("Caffe in Grani", 5, "kg", 1),
    ("Farina 00", 30, "kg", 5),
]

MENU = {
    "Spaghetti alla Carbonara": [
        ("Pasta Spaghetti", 0.1),
        ("Guanciale", 0.05),
        ("Uova", 2),
        ("Pecorino Romano", 0.02),
        ("Pepe Nero", 0.002),
    ],
    "Penne all'Arrabbiata": [
        ("Pasta Penne", 0.1),
        ("Passata di Pomodoro", 0.08),
        ("Aglio", 0.01),
        ("Pepe Nero", 0.001),
        ("Olio Extravergine", 0.01),
    ],
    "Risotto ai Funghi": [
        ("Riso Carnaroli", 0.08),
        ("Funghi Porcini", 0.04),
        ("Parmigiano Reggiano", 0.02),
        ("Olio Extravergine", 0.01),
        ("Vino Bianco Vernaccia", 0.02),
    ],
    "Margherita DOP": [
        ("Farina 00", 0.15),
        ("Pomodori Pelati", 0.06),
        ("Mozzarella Fior di Latte", 0.08),
        ("Basilico Fresco", 0.005),
        ("Olio Extravergine", 0.01),
    ],
    "Bufala e Crudo": [
        ("Farina 00", 0.15),
        ("Pomodori Pelati", 0.06),
        ("Bufala Campana", 0.08),
        ("Prosciutto Crudo", 0.05),
        ("Basilico Fresco", 0.005),
    ],
    "Amatriciana": [
        ("Pasta Spaghetti", 0.1),
        ("Guanciale", 0.05),
        ("Pomodori Pelati", 0.08),
        ("Pecorino Romano", 0.02),
        ("Olio Extravergine", 0.01),
    ],
    "Cacio e Pepe": [
        ("Pasta Spaghetti", 0.1),
        ("Pecorino Romano", 0.03),
        ("Pepe Nero", 0.005),
    ],
    "Risotto alla Milanese": [
        ("Riso Carnaroli", 0.08),
        ("Parmigiano Reggiano", 0.02),
        ("Olio Extravergine", 0.01),
        ("Vino Bianco Vernaccia", 0.01),
    ],
    "Tiramisu": [
        ("Uova", 2),
        ("Caffe in Grani", 0.01),
        ("Mascarpone", 0.05),
    ],
    "Panna Cotta": [
        ("Panna Fresca", 0.05),
        ("Zucchero", 0.02),
        ("Vaniglia", 0.001),
    ],
}

PIATTI = list(MENU.keys())


def api_post(path, payload):
    url = f"{ENDPOINT}{path}"
    r = requests.post(url, headers=HEADERS, json=payload, timeout=15)
    return r


def api_get(path, params=None):
    url = f"{ENDPOINT}{path}"
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    return r


def api_delete(path):
    url = f"{ENDPOINT}{path}"
    r = requests.delete(url, headers=HEADERS, timeout=15)
    return r


def clear_collection(coll):
    offset = 0
    deleted = 0
    while True:
        r = api_get(f"/databases/{DB_ID}/collections/{coll}/documents", {"limit": 25, "offset": offset})
        if r.status_code != 200:
            break
        docs = r.json().get("documents", [])
        if not docs:
            break
        for d in docs:
            rd = api_delete(f"/databases/{DB_ID}/collections/{coll}/documents/{d['$id']}")
            if rd.status_code in (204, 200):
                deleted += 1
        if len(docs) < 25:
            break
        offset += 25
    return deleted


def create_doc(coll, data):
    r = api_post(f"/databases/{DB_ID}/collections/{coll}/documents", {
        "documentId": "unique()",
        "data": data,
    })
    return r.status_code in (201, 200)


def seed_prodotti():
    print("📦 Prodotti...")
    for nome, qty, unita, soglia in PRODOTTI:
        create_doc("prodotti", {
            "prodotto": nome,
            "quantita_attuale": float(qty),
            "unita": unita,
            "soglia_riordino": float(soglia),
        })
    print(f"   ✅ {len(PRODOTTI)} prodotti creati")


def seed_menu():
    print("🍽️ Menu...")
    count = 0
    for piatto, ingredienti in MENU.items():
        for ing, qty in ingredienti:
            create_doc("menu", {
                "piatto": piatto,
                "prodotto": ing,
                "quantita_prodotto": float(qty),
            })
            count += 1
    print(f"   ✅ {count} ingredienti in {len(MENU)} piatti")


def seed_vendite():
    print("🧾 Vendite...")
    vendite = []
    oggi = datetime.now()
    for i in range(14):  # ultimi 14 giorni
        giorno = oggi - timedelta(days=i)
        data_str = giorno.strftime("%Y-%m-%d")
        n_vendite = random.randint(3, 8)
        for _ in range(n_vendite):
            piatto = random.choice(PIATTI)
            qty = random.randint(2, 15)
            vendite.append({"data": data_str, "piatto": piatto, "quantita_venduta": qty})
    for v in vendite:
        create_doc("vendite", v)
    print(f"   ✅ {len(vendite)} vendite create")


def seed_consumi():
    print("🧮 Calcolo consumi...")
    r1 = api_get(f"/databases/{DB_ID}/collections/vendite/documents")
    r2 = api_get(f"/databases/{DB_ID}/collections/menu/documents")
    if r1.status_code != 200 or r2.status_code != 200:
        print("   ⚠️ Errore lettura dati")
        return
    vendite = r1.json().get("documents", [])
    menu = r2.json().get("documents", [])
    consumi = {}
    for v in vendite:
        ricetta = [m for m in menu if m.get("piatto") == v.get("piatto")]
        for r in ricetta:
            key = (v.get("data"), r.get("prodotto"))
            if key not in consumi:
                consumi[key] = 0
            consumi[key] += v.get("quantita_venduta", 0) * r.get("quantita_prodotto", 0)
    for (data, prodotto), qty in consumi.items():
        create_doc("consumi", {
            "data": data,
            "prodotto": prodotto,
            "quantita_consumata": round(qty, 3),
            "fonte": "vendita",
        })
    print(f"   ✅ {len(consumi)} consumi calcolati")


def seed_ordini():
    print("📋 Ordini...")
    r = api_post(f"/databases/{DB_ID}/collections/ordini/documents", {
        "documentId": "unique()",
        "data": {
            "data_ordine": datetime.now().strftime("%Y-%m-%d"),
            "fornitore": "Rossi Food Supply",
            "stato": "bozza",
            "note": "Ordine settimanale"
        }
    })
    if r.status_code in (201, 200):
        ordine_id = r.json()["$id"]
        items = [
            ("Olio Extravergine", 10),
            ("Parmigiano Reggiano", 5),
            ("Pasta Spaghetti", 20),
            ("Uova", 200),
        ]
        for nome, qty in items:
            create_doc("ordini_items", {
                "ordine_id": ordine_id,
                "prodotto": nome,
                "quantita_ordinata": float(qty),
                "quantita_ricevuta": 0,
                "ricevuto": False,
            })
        print(f"   ✅ 1 ordine con {len(items)} articoli")


def main():
    print("🌱 Seed dati demo\n")
    print("🗑️ Cancellazione dati esistenti...")
    for coll in ["prodotti", "menu", "vendite", "consumi", "ordini", "ordini_items"]:
        n = clear_collection(coll)
        print(f"   🗑️ {coll}: {n} eliminati")
    print()
    seed_prodotti()
    seed_menu()
    seed_vendite()
    seed_consumi()
    seed_ordini()
    print("\n✨ Seed completato!")


if __name__ == "__main__":
    main()
