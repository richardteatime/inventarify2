#!/usr/bin/env python3
"""
Script di setup per Inventarify su Appwrite (qualsiasi versione).
Usa HTTP REST diretto per massima compatibilità.

Uso:
    export APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
    export APPWRITE_PROJECT=xxxxxxxx
    export APPWRITE_API_KEY=xxxxxxxx
    python scripts/setup-appwrite.py
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
DB_NAME = "Inventarify Database"

COLLECTIONS = {
    "prodotti": {
        "attributes": [
            {"key": "prodotto", "type": "string", "size": 255, "required": True},
            {"key": "quantita_attuale", "type": "float", "required": True},
            {"key": "unita", "type": "string", "size": 50, "required": True},
            {"key": "soglia_riordino", "type": "float", "required": True},
            {"key": "fornitore", "type": "string", "size": 255, "required": False},
            {"key": "costo_unitario", "type": "float", "required": False},
            {"key": "note", "type": "string", "size": 1000, "required": False},
        ],
        "indexes": [
            {"key": "idx_prodotto", "type": "key", "attributes": ["prodotto"]},
        ]
    },
    "menu": {
        "attributes": [
            {"key": "piatto", "type": "string", "size": 255, "required": True},
            {"key": "prodotto", "type": "string", "size": 255, "required": True},
            {"key": "quantita_prodotto", "type": "float", "required": True},
            {"key": "porzione_default", "type": "integer", "required": False},
        ],
        "indexes": [
            {"key": "idx_piatto", "type": "key", "attributes": ["piatto"]},
        ]
    },
    "vendite": {
        "attributes": [
            {"key": "data", "type": "string", "size": 50, "required": True},
            {"key": "piatto", "type": "string", "size": 255, "required": True},
            {"key": "quantita_venduta", "type": "integer", "required": True},
            {"key": "turno", "type": "string", "size": 20, "required": False},
        ],
        "indexes": [
            {"key": "idx_data", "type": "key", "attributes": ["data"]},
        ]
    },
    "ordini": {
        "attributes": [
            {"key": "data_ordine", "type": "string", "size": 50, "required": True},
            {"key": "fornitore", "type": "string", "size": 255, "required": False},
            {"key": "stato", "type": "string", "size": 50, "required": True},
            {"key": "note", "type": "string", "size": 1000, "required": False},
        ],
        "indexes": [
            {"key": "idx_stato", "type": "key", "attributes": ["stato"]},
        ]
    },
    "ordini_items": {
        "attributes": [
            {"key": "ordine_id", "type": "string", "size": 255, "required": True},
            {"key": "prodotto", "type": "string", "size": 255, "required": True},
            {"key": "quantita_ordinata", "type": "float", "required": True},
            {"key": "quantita_ricevuta", "type": "float", "required": False},
            {"key": "ricevuto", "type": "boolean", "required": False},
        ],
        "indexes": [
            {"key": "idx_ordine", "type": "key", "attributes": ["ordine_id"]},
        ]
    },
    "consumi": {
        "attributes": [
            {"key": "data", "type": "string", "size": 50, "required": True},
            {"key": "prodotto", "type": "string", "size": 255, "required": True},
            {"key": "quantita_consumata", "type": "float", "required": True},
            {"key": "fonte", "type": "string", "size": 255, "required": True},
        ],
        "indexes": [
            {"key": "idx_data_consumi", "type": "key", "attributes": ["data"]},
        ]
    },
}

BUCKETS = {
    "vendite-csv": "Upload CSV vendite",
    "ordini-csv": "Upload CSV ordini",
}

PERMISSIONS = [
    'read("users")',
    'create("users")',
    'update("users")',
    'delete("users")',
]


def api_post(path, payload):
    url = f"{ENDPOINT}{path}"
    r = requests.post(url, headers=HEADERS, json=payload)
    return r


def api_get(path):
    url = f"{ENDPOINT}{path}"
    r = requests.get(url, headers=HEADERS)
    return r


def create_database():
    r = api_post("/databases", {"databaseId": DB_ID, "name": DB_NAME, "permissions": PERMISSIONS})
    if r.status_code in (201, 200):
        print(f"✅ Database '{DB_ID}' creato")
    elif r.status_code == 409:
        print(f"ℹ️ Database '{DB_ID}' esiste già")
    else:
        print(f"❌ Errore database: {r.status_code} {r.text[:200]}")


def create_collection(coll_id, config):
    r = api_post(f"/databases/{DB_ID}/collections", {
        "collectionId": coll_id,
        "name": coll_id,
        "permissions": PERMISSIONS,
    })
    if r.status_code in (201, 200):
        print(f"  ✅ Collection '{coll_id}' creata")
    elif r.status_code == 409:
        print(f"  ℹ️ Collection '{coll_id}' esiste già")
    else:
        print(f"  ❌ Errore collection {coll_id}: {r.status_code} {r.text[:200]}")
        return

    # Attributes
    for attr in config.get("attributes", []):
        attr_type = attr["type"]
        payload = {
            "key": attr["key"],
            "required": attr["required"],
        }
        if attr_type in ("string",):
            payload["size"] = attr.get("size", 255)

        r2 = api_post(f"/databases/{DB_ID}/collections/{coll_id}/attributes/{attr_type}", payload)
        if r2.status_code in (201, 200, 202):
            print(f"    ✅ Attributo '{attr['key']}' ({attr_type})")
        elif r2.status_code == 409:
            print(f"    ℹ️ Attributo '{attr['key']}' esiste già")
        else:
            print(f"    ❌ Errore attributo {attr['key']}: {r2.status_code} {r2.text[:200]}")

    # Indexes (wait a bit for attributes to be processed)
    time.sleep(2)
    for idx in config.get("indexes", []):
        r3 = api_post(f"/databases/{DB_ID}/collections/{coll_id}/indexes", {
            "key": idx["key"],
            "type": idx["type"],
            "attributes": idx["attributes"],
        })
        if r3.status_code in (201, 200, 202):
            print(f"    ✅ Index '{idx['key']}'")
        elif r3.status_code == 409:
            print(f"    ℹ️ Index '{idx['key']}' esiste già")
        else:
            print(f"    ❌ Errore index {idx['key']}: {r3.status_code} {r3.text[:200]}")


def create_buckets():
    for bucket_id, bucket_name in BUCKETS.items():
        r = api_post("/storage/buckets", {
            "bucketId": bucket_id,
            "name": bucket_name,
            "permissions": PERMISSIONS,
            "fileSecurity": False,
        })
        if r.status_code in (201, 200):
            print(f"✅ Bucket '{bucket_id}' creato")
        elif r.status_code == 409:
            print(f"ℹ️ Bucket '{bucket_id}' esiste già")
        else:
            print(f"❌ Errore bucket {bucket_id}: {r.status_code} {r.text[:200]}")


def main():
    print("🔧 Setup Inventarify su Appwrite\n")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Project:  {PROJECT}\n")

    create_database()
    print()

    for coll_id, config in COLLECTIONS.items():
        print(f"📦 Collection: {coll_id}")
        create_collection(coll_id, config)
        print()

    print("📁 Storage Buckets:")
    create_buckets()
    print()

    print("✨ Setup completato!")
    print(f"\nProssimo passo:")
    print(f"  1. Configura frontend/.env con:")
    print(f"     PUBLIC_APPWRITE_ENDPOINT={ENDPOINT}")
    print(f"     PUBLIC_APPWRITE_PROJECT={PROJECT}")
    print(f"     PUBLIC_APPWRITE_DATABASE_ID={DB_ID}")
    print(f"  2. Esegui: python scripts/migrate-data.py")


if __name__ == "__main__":
    main()
