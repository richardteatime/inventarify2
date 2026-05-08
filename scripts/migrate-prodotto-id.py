#!/usr/bin/env python3
"""
Aggiunge l'attributo 'prodotto_id' alle collections menu, ordini_items, consumi
e migra i dati esistenti facendo match per nome con la collection prodotti.

Uso:
    export APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
    export APPWRITE_PROJECT=xxxxxxxx
    export APPWRITE_API_KEY=xxxxxxxx
    python scripts/migrate-prodotto-id.py
"""

import os
import sys
import json
import time
import requests

ENDPOINT = os.environ.get("APPWRITE_ENDPOINT", "").rstrip("/")
PROJECT = os.environ.get("APPWRITE_PROJECT", "")
API_KEY = os.environ.get("APPWRITE_API_KEY", "")

if not ENDPOINT or not PROJECT or not API_KEY:
    print("❌ Imposta APPWRITE_ENDPOINT, APPWRITE_PROJECT e APPWRITE_API_KEY")
    sys.exit(1)

HEADERS = {
    "X-Appwrite-Project": PROJECT,
    "X-Appwrite-Key": API_KEY,
    "Content-Type": "application/json",
}

DB_ID = "inventarify"


def api_get(path, params=None):
    url = f"{ENDPOINT}{path}"
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def api_post(path, payload):
    url = f"{ENDPOINT}{path}"
    r = requests.post(url, headers=HEADERS, json=payload)
    return r


def api_patch(path, payload):
    url = f"{ENDPOINT}{path}"
    r = requests.patch(url, headers=HEADERS, json=payload)
    return r


def add_attribute(collection_id, key):
    """Aggiunge attributo stringa opzionale."""
    r = api_post(f"/databases/{DB_ID}/collections/{collection_id}/attributes/string", {
        "key": key,
        "size": 255,
        "required": False,
    })
    if r.status_code in (201, 200, 202):
        print(f"  ✅ Attributo '{key}' aggiunto a '{collection_id}'")
        return True
    elif r.status_code == 409:
        print(f"  ℹ️ Attributo '{key}' esiste già in '{collection_id}'")
        return True
    else:
        print(f"  ❌ Errore aggiungendo '{key}' a '{collection_id}': {r.status_code} {r.text[:200]}")
        return False


def list_all_documents(collection_id, limit=100):
    docs = []
    offset = 0
    while True:
        r = api_get(f"/databases/{DB_ID}/collections/{collection_id}/documents", {
            "limit": limit,
            "offset": offset
        })
        if r.status_code != 200:
            print(f"  ❌ Errore leggendo {collection_id}: {r.status_code}")
            break
        batch = r.json().get("documents", [])
        if not batch:
            break
        docs.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return docs


def update_document(collection_id, doc_id, data):
    r = api_patch(f"/databases/{DB_ID}/collections/{collection_id}/documents/{doc_id}", {"data": data})
    return r.status_code in (200, 202)


def main():
    print("🔧 Aggiunta attributo prodotto_id\n")

    collections = ["menu", "ordini_items", "consumi"]
    for coll in collections:
        add_attribute(coll, "prodotto_id")

    # Aspetta che gli attributi siano processati
    print("\n⏳ Attendo 3 secondi per il processing attributi...")
    time.sleep(3)

    # Carica tutti i prodotti per fare il mapping nome -> id
    print("\n📦 Caricamento prodotti...")
    prodotti = list_all_documents("prodotti")
    prodotto_by_name = {}
    for p in prodotti:
        name = p.get("prodotto", "").strip()
        pid = p.get("$id", "")
        if name and pid:
            prodotto_by_name[name] = pid
    print(f"   {len(prodotto_by_name)} prodotti caricati")

    # Migra menu
    print("\n🍽️  Migrazione menu...")
    menu_docs = list_all_documents("menu")
    updated = 0
    skipped = 0
    for doc in menu_docs:
        if doc.get("prodotto_id"):
            skipped += 1
            continue
        name = doc.get("prodotto", "").strip()
        pid = prodotto_by_name.get(name)
        if pid:
            if update_document("menu", doc["$id"], {"prodotto_id": pid}):
                updated += 1
            else:
                print(f"   ⚠️  Fallito update {doc['$id']}")
        else:
            print(f"   ⚠️  Prodotto non trovato: '{name}' (doc {doc['$id']})")
    print(f"   Aggiornati: {updated}, già con ID: {skipped}")

    # Migra ordini_items
    print("\n📋 Migrazione ordini_items...")
    items_docs = list_all_documents("ordini_items")
    updated = 0
    skipped = 0
    for doc in items_docs:
        if doc.get("prodotto_id"):
            skipped += 1
            continue
        name = doc.get("prodotto", "").strip()
        pid = prodotto_by_name.get(name)
        if pid:
            if update_document("ordini_items", doc["$id"], {"prodotto_id": pid}):
                updated += 1
            else:
                print(f"   ⚠️  Fallito update {doc['$id']}")
        else:
            print(f"   ⚠️  Prodotto non trovato: '{name}' (doc {doc['$id']})")
    print(f"   Aggiornati: {updated}, già con ID: {skipped}")

    # Migra consumi
    print("\n📉 Migrazione consumi...")
    consumi_docs = list_all_documents("consumi")
    updated = 0
    skipped = 0
    for doc in consumi_docs:
        if doc.get("prodotto_id"):
            skipped += 1
            continue
        name = doc.get("prodotto", "").strip()
        pid = prodotto_by_name.get(name)
        if pid:
            if update_document("consumi", doc["$id"], {"prodotto_id": pid}):
                updated += 1
            else:
                print(f"   ⚠️  Fallito update {doc['$id']}")
        else:
            print(f"   ⚠️  Prodotto non trovato: '{name}' (doc {doc['$id']})")
    print(f"   Aggiornati: {updated}, già con ID: {skipped}")

    print("\n✅ Migrazione completata!")


if __name__ == "__main__":
    main()
