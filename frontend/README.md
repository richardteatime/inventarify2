# Inventarify Frontend

Frontend SvelteKit per Inventarify — gestione magazzino ristorante.

## Stack
- **SvelteKit** + TypeScript
- **Tailwind CSS** con design token da `DESIGN.md`
- **Appwrite** (auth, database, storage)

## Setup

```bash
cd frontend
npm install
```

## Configura ambiente

```bash
cp .env.example .env
# Modifica .env con i tuoi dati Appwrite
```

## Sviluppo locale

```bash
npm run dev
```

L'app sarà su `http://localhost:5173`

## Build produzione

```bash
npm run build
npm run preview
```

## Deploy (Coolify)

Il `Dockerfile` è già configurato. Su Coolify:
1. Nuovo Service → Dockerfile
2. Point al repo, path `frontend/`
3. Variabili d'ambiente da `.env`
4. Deploy

## Setup Appwrite

1. Crea un progetto su Appwrite
2. Genera una API Key con permessi `database`, `storage`, `auth`
3. Esegui lo script di setup:

```bash
export APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
export APPWRITE_PROJECT=xxxxxxxx
export APPWRITE_API_KEY=xxxxxxxx
python scripts/setup-appwrite.py
```

4. Migra i dati CSV:

```bash
python scripts/migrate-data.py
```
