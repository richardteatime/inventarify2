#!/usr/bin/env python3
"""
Script di setup per Inventarify su Appwrite.
Crea database, collections, attributi e permessi.

Uso:
    export APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
    export APPWRITE_PROJECT=xxxxxxxx
    export APPWRITE_API_KEY=xxxxxxxx
    python scripts/setup-appwrite.py
"""

import os
import sys

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID

ENDPOINT = os.environ.get("APPWRITE_ENDPOINT", "https://appwrite.tuodominio.it/v1")
PROJECT = os.environ.get("APPWRITE_PROJECT", "")
API_KEY = os.environ.get("APPWRITE_API_KEY", "")

if not PROJECT or not API_KEY:
    print("❌ Imposta APPWRITE_PROJECT e APPWRITE_API_KEY come variabili d'ambiente")
    sys.exit(1)

client = Client()
client.set_endpoint(ENDPOINT)
client.set_project(PROJECT)
client.set_key(API_KEY)

databases = Databases(client)
storage = Storage(client)

DB_ID = "inventarify"
DB_NAME = "Inventarify Database"

COLLECTIONS = {
    "prodotti": {
        "attributes": [
            ("prodotto", "string", 255, True),
            ("quantità_attuale", "double", None, True),
            ("unità", "string", 50, True),
            ("soglia_riordino", "double", None, True),
            ("fornitore", "string", 255, False),
            ("costo_unitario", "double", None, False),
            ("note", "string", 1000, False),
        ],
        "indexes": [
            ("idx_prodotto", "key", ["prodotto"]),
        ]
    },
    "menu": {
        "attributes": [
            ("piatto", "string", 255, True),
            ("prodotto", "string", 255, True),
            ("quantità_prodotto", "double", None, True),
            ("porzione_default", "integer", None, False),
        ],
        "indexes": [
            ("idx_piatto", "key", ["piatto"]),
            ("idx_piatto_prodotto", "key", ["piatto", "prodotto"]),
        ]
    },
    "vendite": {
        "attributes": [
            ("data", "string", 50, True),
            ("piatto", "string", 255, True),
            ("quantità_venduta", "integer", None, True),
            ("turno", "string", 20, False),
        ],
        "indexes": [
            ("idx_data", "key", ["data"]),
            ("idx_piatto", "key", ["piatto"]),
        ]
    },
    "ordini": {
        "attributes": [
            ("data_ordine", "string", 50, True),
            ("fornitore", "string", 255, False),
            ("stato", "string", 50, True),
            ("note", "string", 1000, False),
        ],
        "indexes": [
            ("idx_stato", "key", ["stato"]),
        ]
    },
    "ordini_items": {
        "attributes": [
            ("ordine_id", "string", 255, True),
            ("prodotto", "string", 255, True),
            ("quantità_ordinata", "double", None, True),
            ("quantità_ricevuta", "double", None, False),
            ("ricevuto", "boolean", None, False),
        ],
        "indexes": [
            ("idx_ordine", "key", ["ordine_id"]),
        ]
    },
    "consumi": {
        "attributes": [
            ("data", "string", 50, True),
            ("prodotto", "string", 255, True),
            ("quantità_consumata", "double", None, True),
            ("fonte", "string", 255, True),
        ],
        "indexes": [
            ("idx_data", "key", ["data"]),
            ("idx_prodotto", "key", ["prodotto"]),
        ]
    },
}

BUCKETS = {
    "vendite-csv": "Upload CSV vendite",
    "ordini-csv": "Upload CSV ordini",
}

PERMISSIONS = [
    Permission.read(Role.users()),
    Permission.create(Role.users()),
    Permission.update(Role.users()),
    Permission.delete(Role.users()),
]


def create_database():
    try:
        db = databases.create(DB_ID, DB_NAME)
        print(f"✅ Database creato: {db['$id']}")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"ℹ️ Database '{DB_ID}' esiste già")
        else:
            print(f"❌ Errore database: {e}")


def create_collection(coll_id, config):
    try:
        coll = databases.create_collection(DB_ID, coll_id, coll_id, PERMISSIONS)
        print(f"  ✅ Collection '{coll_id}' creata")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"  ℹ️ Collection '{coll_id}' esiste già")
        else:
            print(f"  ❌ Errore collection {coll_id}: {e}")
            return

    # Create attributes
    for attr in config.get("attributes", []):
        name, type_, size_or_default, required = attr
        try:
            if type_ == "string":
                databases.create_string_attribute(DB_ID, coll_id, name, size_or_default, required)
            elif type_ == "integer":
                databases.create_integer_attribute(DB_ID, coll_id, name, required)
            elif type_ == "double":
                databases.create_float_attribute(DB_ID, coll_id, name, required)
            elif type_ == "boolean":
                databases.create_boolean_attribute(DB_ID, coll_id, name, required)
            print(f"    ✅ Attributo '{name}' ({type_})")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"    ℹ️ Attributo '{name}' esiste già")
            else:
                print(f"    ❌ Errore attributo {name}: {e}")

    # Create indexes
    for idx in config.get("indexes", []):
        idx_name, idx_type, attrs = idx
        try:
            databases.create_index(DB_ID, coll_id, idx_name, idx_type, attrs)
            print(f"    ✅ Index '{idx_name}'")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"    ℹ️ Index '{idx_name}' esiste già")
            else:
                print(f"    ❌ Errore index {idx_name}: {e}")


def create_buckets():
    for bucket_id, bucket_name in BUCKETS.items():
        try:
            storage.create_bucket(
                bucket_id,
                bucket_name,
                permissions=PERMISSIONS,
                file_security=False,
            )
            print(f"✅ Bucket '{bucket_id}' creato")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"ℹ️ Bucket '{bucket_id}' esiste già")
            else:
                print(f"❌ Errore bucket {bucket_id}: {e}")


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
