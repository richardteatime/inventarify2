#!/usr/bin/env python3
"""
Migrazione dati CSV MVP → Appwrite.

Uso:
    export APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
    export APPWRITE_PROJECT=xxxxxxxx
    export APPWRITE_API_KEY=xxxxxxxx
    python scripts/migrate-data.py
"""

import os
import sys
import csv

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

ENDPOINT = os.environ.get("APPWRITE_ENDPOINT", "https://appwrite.tuodominio.it/v1")
PROJECT = os.environ.get("APPWRITE_PROJECT", "")
API_KEY = os.environ.get("APPWRITE_API_KEY", "")
DB_ID = "inventarify"

if not PROJECT or not API_KEY:
    print("❌ Imposta APPWRITE_PROJECT e APPWRITE_API_KEY")
    sys.exit(1)

client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT)
client.set_key(API_KEY)

databases = Databases(client)


def read_csv(filename):
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    if not os.path.exists(path):
        print(f"⚠️ File non trovato: {path}")
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def migrate_prodotti():
    rows = read_csv("prodotti_magazzino.csv")
    if not rows:
        return
    print(f"📦 Prodotti: {len(rows)} righe...")
    for row in rows:
        try:
            databases.create_document(DB_ID, "prodotti", ID.unique(), {
                "prodotto": row["prodotto"],
                "quantità_attuale": float(row["quantità_attuale"]),
                "unità": row["unità"],
                "soglia_riordino": float(row["soglia_riordino"]),
            })
        except Exception as e:
            print(f"  ❌ {row.get('prodotto')}: {e}")
    print("  ✅ Prodotti migrati")


def migrate_menu():
    rows = read_csv("menu.csv")
    if not rows:
        return
    print(f"🍽️ Menu: {len(rows)} righe...")
    for row in rows:
        try:
            databases.create_document(DB_ID, "menu", ID.unique(), {
                "piatto": row["piatto"],
                "prodotto": row["prodotto"],
                "quantità_prodotto": float(row["quantità_prodotto"]),
            })
        except Exception as e:
            print(f"  ❌ {row.get('piatto')}: {e}")
    print("  ✅ Menu migrato")


def migrate_vendite():
    rows = read_csv("vendite.csv")
    if not rows:
        return
    print(f"🧾 Vendite: {len(rows)} righe...")
    for row in rows:
        try:
            databases.create_document(DB_ID, "vendite", ID.unique(), {
                "data": row["data"],
                "piatto": row["piatto"],
                "quantità_venduta": int(row["quantità_venduta"]),
            })
        except Exception as e:
            print(f"  ❌ {row.get('piatto')}: {e}")
    print("  ✅ Vendite migrate")


def migrate_consumi():
    """Calcola consumi da vendite × menu e li salva."""
    print("🧮 Calcolo consumi...")
    vendite = []
    menu = []
    try:
        vendite_res = databases.list_documents(DB_ID, "vendite")
        vendite = vendite_res["documents"]
        menu_res = databases.list_documents(DB_ID, "menu")
        menu = menu_res["documents"]
    except Exception as e:
        print(f"  ❌ Errore lettura dati: {e}")
        return

    consumi = {}
    for v in vendite:
        ricetta = [m for m in menu if m["piatto"] == v["piatto"]]
        for r in ricetta:
            key = (v["data"], r["prodotto"])
            if key not in consumi:
                consumi[key] = 0
            consumi[key] += v["quantità_venduta"] * r["quantità_prodotto"]

    for (data, prodotto), qty in consumi.items():
        try:
            databases.create_document(DB_ID, "consumi", ID.unique(), {
                "data": data,
                "prodotto": prodotto,
                "quantità_consumata": round(qty, 3),
                "fonte": "vendita",
            })
        except Exception as e:
            print(f"  ❌ {prodotto}: {e}")

    print(f"  ✅ {len(consumi)} consumi calcolati e salvati")


def main():
    print("🚀 Migrazione dati MVP → Appwrite\n")
    migrate_prodotti()
    migrate_menu()
    migrate_vendite()
    migrate_consumi()
    print("\n✨ Migrazione completata!")


if __name__ == "__main__":
    main()
