#!/usr/bin/env python3
"""
Migrazione dati CSV MVP → Appwrite (HTTP REST diretto).

Uso:
    export APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
    export APPWRITE_PROJECT=xxxxxxxx
    export APPWRITE_API_KEY=xxxxxxxx
    python scripts/migrate-data.py
"""

import os
import sys
import csv
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


def api_post(path, payload):
    url = f"{ENDPOINT}{path}"
    r = requests.post(url, headers=HEADERS, json=payload)
    return r


def api_get(path, params=None):
    url = f"{ENDPOINT}{path}"
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def read_csv(filename):
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    if not os.path.exists(path):
        print(f"⚠️ File non trovato: {path}")
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


PERMISSIONS = ['read("users")', 'update("users")', 'delete("users")']

def create_doc(collection, data):
    r = api_post(f"/databases/{DB_ID}/collections/{collection}/documents", {
        "documentId": "unique()",
        "data": data,
        "permissions": PERMISSIONS,
    })
    return r.status_code in (201, 200)


def migrate_prodotti():
    rows = read_csv("prodotti_magazzino.csv")
    if not rows:
        return
    print(f"📦 Prodotti: {len(rows)} righe...")
    for row in rows:
        ok = create_doc("prodotti", {
            "prodotto": row["prodotto"],
            "quantita_attuale": float(row["quantità_attuale"]),
            "unita": row["unità"],
            "soglia_riordino": float(row["soglia_riordino"]),
        })
        if not ok:
            print(f"  ❌ Errore: {row.get('prodotto')}")
    print("  ✅ Prodotti migrati")


def migrate_menu():
    rows = read_csv("menu.csv")
    if not rows:
        return
    print(f"🍽️ Menu: {len(rows)} righe...")
    for row in rows:
        ok = create_doc("menu", {
            "piatto": row["piatto"],
            "prodotto": row["prodotto"],
            "quantita_prodotto": float(row["quantità_prodotto"]),
        })
        if not ok:
            print(f"  ❌ Errore: {row.get('piatto')}")
    print("  ✅ Menu migrato")


def migrate_vendite():
    rows = read_csv("vendite.csv")
    if not rows:
        return
    print(f"🧾 Vendite: {len(rows)} righe...")
    for row in rows:
        ok = create_doc("vendite", {
            "data": row["data"],
            "piatto": row["piatto"],
            "quantita_venduta": int(row["quantità_venduta"]),
        })
        if not ok:
            print(f"  ❌ Errore: {row.get('piatto')}")
    print("  ✅ Vendite migrate")


def migrate_consumi():
    print("🧮 Calcolo consumi...")
    vendite = []
    menu = []

    r1 = api_get(f"/databases/{DB_ID}/collections/vendite/documents")
    if r1.status_code == 200:
        vendite = r1.json().get("documents", [])

    r2 = api_get(f"/databases/{DB_ID}/collections/menu/documents")
    if r2.status_code == 200:
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
        ok = create_doc("consumi", {
            "data": data,
            "prodotto": prodotto,
            "quantita_consumata": round(qty, 3),
            "fonte": "vendita",
        })
        if not ok:
            print(f"  ❌ Errore consumo: {prodotto}")

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
