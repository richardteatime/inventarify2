# 🧠 Inventarify — Sistema Intelligente di Gestione Magazzino

Applicazione di gestione magazzino per ristoranti. **MVP** in Streamlit → **v2** in SvelteKit + Appwrite.

---

## 🏗️ Architettura

| Livello | Tecnologia | Host |
|---------|-----------|------|
| **Frontend** | SvelteKit + Tailwind + TypeScript | Coolify (Hetzner) |
| **Backend** | Appwrite (Auth, DB, Storage) | Coolify (Hetzner) |
| **Deploy** | Docker container | Coolify |

---

## 📁 Struttura progetto

```
├── frontend/          ← Nuova app v2 (SvelteKit)
│   ├── Dockerfile
│   ├── src/
│   └── ...
├── scripts/           ← Setup Appwrite + migrazione dati
│   ├── setup-appwrite.py
│   └── migrate-data.py
├── app.py             ← MVP Streamlit (legacy)
├── *.csv              ← Dati MVP (legacy)
└── DESIGN.md          ← Design system
```

---

## 🚀 Deploy su Coolify (Step-by-step)

### 1. Configura Appwrite (già su Coolify)

Vai sulla console Appwrite del tuo server:

```
Project Settings → Platforms → Add Platform → Web App
  Name: Inventarify
  Hostname: inventarify.tuo-dominio.it   (o il tuo dominio)
```

**Project Settings → Security → CORS**: aggiungi il tuo dominio di produzione.

### 2. Setup collections e dati

```bash
# Installa SDK Python
pip install appwrite

# Configura credenziali
export APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
export APPWRITE_PROJECT=tuo-project-id
export APPWRITE_API_KEY=tua-api-key

# Crea database, collections, buckets
python scripts/setup-appwrite.py

# Migra dati CSV del MVP
python scripts/migrate-data.py
```

### 3. Deploy frontend su Coolify

Su Coolify:

1. **Add Resource** → **Dockerfile**
2. Seleziona il repository GitHub `richardteatime/inventarify2`
3. **Base Directory**: `frontend/`
4. **Port**: `3000`
5. **Environment Variables**:

| Chiave | Valore |
|--------|--------|
| `PUBLIC_APPWRITE_ENDPOINT` | `https://appwrite.tuodominio.it/v1` |
| `PUBLIC_APPWRITE_PROJECT` | `tuo-project-id` |
| `PUBLIC_APPWRITE_DATABASE_ID` | `inventarify` |

6. **Domains**: `inventarify.tuo-dominio.it`
7. **Deploy**

---

## 💻 Sviluppo locale (opzionale)

Se vuoi sviluppare in locale prima di deployare:

```bash
cd frontend
npm install

# Crea .env locale
cp .env.example .env
# Modifica con il tuo endpoint Appwrite remoto

npm run dev
```

> Il frontend in locale si connette direttamente ad Appwrite sul tuo server Hetzner.
> Ricorda di aggiungere `localhost:5173` nei platform di Appwrite per CORS.

---

## 🧾 Dati legacy (MVP)

I file CSV nella root sono i dati originali del MVP Streamlit:
- `menu.csv` — ricette piatti
- `prodotti_magazzino.csv` — scorte iniziali
- `vendite.csv` — storico vendite

Usa `scripts/migrate-data.py` per importarli in Appwrite.

---

## 🎨 Design System

Vedi `DESIGN.md` — design language "Shopifi Inspired" implementato in Tailwind CSS:
- Dual canvas: dark per marketing, light/cream per transazionale
- Pill buttons (forma non negoziabile)
- Thin display typography (Inter 300)
- Accent aloe/pistachio

---

## 🛠️ Stack completo

- **Frontend**: SvelteKit 5, TypeScript, Tailwind CSS
- **Backend**: Appwrite (self-hosted)
- **Database**: Appwrite Document Store
- **Auth**: Appwrite Auth (email/password)
- **Storage**: Appwrite Storage (CSV upload)
- **Deploy**: Docker + Coolify + Hetzner
