# 🚀 Piano di Trasformazione MVP → App Reale

## Inventarify v2 — Sistema di Gestione Magazzino per Ristoranti

---

## 1. Stack Tecnologico

| Livello | Tecnologia | Motivazione |
|---------|-----------|-------------|
| **Frontend** | **SvelteKit** + TypeScript | Bundle minimo (~30KB), reattività nativa, routing integrato, SSR/SPA flessibile. Ideale per tool interni veloci. |
| **Styling** | Tailwind CSS + design token | Implementazione fedele del DESIGN.md, utility-first, zero CSS morto. |
| **Backend** | **Appwrite** (self-hosted Hetzner/Coolify) | Auth, database, storage, realtime già pronti. Nessun backend da scrivere. |
| **Database** | Appwrite Databases (document store) | Migrazione da SQLite/CSV a collections strutturate. |
| **Deploy** | Coolify (Hetzner) | Container Docker SvelteKit + Appwrite già presente. |

### Perché SvelteKit e non React/Next.js?
- **Bundle 5-10x più piccolo**: un'app gestionale deve caricare in <1s anche su mobile
- **Reattività compile-time**: niente Virtual DOM, performance native
- **Routing file-based**: semplice da mantenere
- **TypeScript first-class**: tipi ovunque senza configurazioni
- **Adatto a SPA interne**: il ristorante non ha bisogno di SEO, una SPA è perfetta

---

## 2. Architettura Appwrite

### 2.1 Database — Collections

```
Database: inventarify
├── collection: prodotti
│   ├── prodotto (string, required, unique)
│   ├── quantità_attuale (float, required)
│   ├── unità (string, required)
│   ├── soglia_riordino (float, required)
│   ├── fornitore (string, optional)
│   ├── costo_unitario (float, optional)
│   └── note (string, optional)
│
├── collection: menu
│   ├── piatto (string, required)
│   ├── prodotto (string, required) → relazione con prodotti
│   ├── quantità_prodotto (float, required)
│   └── porzione_default (int, optional)
│
├── collection: vendite
│   ├── data (datetime, required)
│   ├── piatto (string, required)
│   ├── quantità_venduta (int, required)
│   └── turno (string, optional) → pranzo/cena
│
├── collection: ordini
│   ├── data_ordine (datetime, required)
│   ├── fornitore (string, optional)
│   ├── stato (enum: bozza, inviato, consegnato, parziale)
│   └── note (string, optional)
│
├── collection: ordini_items
│   ├── ordine_id (relationship → ordini)
│   ├── prodotto (string, required)
│   ├── quantità_ordinata (float, required)
│   ├── quantità_ricevuta (float, default 0)
│   └── ricevuto (boolean, default false)
│
├── collection: consumi (auto-generati)
│   ├── data (datetime, required)
│   ├── prodotto (string, required)
│   ├── quantità_consumata (float, required)
│   └── fonte (string) → vendita/aggiornamento_manuale
│
└── collection: utenti_app (estende Appwrite Users)
    ├── ruolo (enum: admin, cuoco, manager)
    ├── ristorante_nome (string)
    └── telefono (string)
```

### 2.2 Storage Buckets

```
├── vendite-csv/      → Upload CSV vendite giornaliere
├── ordini-csv/       → Upload CSV ordini fornitori
├── menu-csv/         → Backup/restore menu
├── magazzino-csv/    → Backup/restore magazzino
└── foto-prodotti/    → (futuro) Immagini prodotti
```

### 2.3 Auth & Permissions

| Ruolo | Permessi |
|-------|----------|
| **Admin** | Tutto: CRUD prodotti, menu, vendite, ordini, utenti |
| **Manager** | CRUD vendite, ordini, lettura magazzino. No utenti. |
| **Cuoco** | Lettura magazzino, lettura menu. No vendite/ordini. |

- **OAuth**: Google (opzionale, facile con Appwrite)
- **Session**: JWT, persistent login
- **Team**: ogni ristorante è un Team Appwrite

---

## 3. Data Migration (MVP → Appwrite)

### Fase 1: Script di migrazione
```python
# scripts/migrate.py
# 1. Legge i CSV esistenti
# 2. Crea collections in Appwrite (se non esistono)
# 3. Inserisce documenti in batch (100/doc per batch)
# 4. Verifica consistenza
```

### Fase 2: Calcolo consumi storici
```python
# Ricostruisce i consumi incrociando vendite × menu
# Popola la collection consumi per avere storico completo
```

---

## 4. Struttura Frontend (SvelteKit)

```
src/
├── app.html                    → HTML base, font loading
├── app.css                     → Tailwind + design tokens CSS custom
├── routes/
│   ├── +layout.svelte          → Root layout, auth check, nav
│   ├── +page.svelte            → Dashboard / Home
│   ├── login/+page.svelte      → Login/Register
│   ├── magazzino/
│   │   ├── +page.svelte        → Lista prodotti, CRUD inline
│   │   └── riordino/+page.svelte → Prodotti sotto soglia, genera ordine
│   ├── menu/
│   │   └── +page.svelte        → Ricette piatti, associazione ingredienti
│   ├── vendite/
│   │   ├── +page.svelte        → Storico vendite
│   │   └── carica/+page.svelte → Upload CSV vendite, preview, conferma
│   ├── ordini/
│   │   ├── +page.svelte        → Lista ordini
│   │   ├── nuovo/+page.svelte  → Crea ordine da riordino
│   │   └── [id]/+page.svelte   → Dettaglio ordine, checklist ricezione
│   └── analytics/
│       └── +page.svelte        → Grafici vendite, consumi, trend
│
├── lib/
│   ├── appwrite.ts             → Client init, constants
│   ├── auth.ts                 → Login, logout, session
│   ├── database/
│   │   ├── prodotti.ts         → CRUD prodotti
│   │   ├── menu.ts             → CRUD menu
│   │   ├── vendite.ts          → CRUD vendite + processa CSV
│   │   ├── ordini.ts           → CRUD ordini + checklist
│   │   └── consumi.ts          → Query consumi aggregati
│   ├── components/
│   │   ├── ui/                 → Button, Input, Card, Badge, Modal (design system)
│   │   ├── layout/             → NavBar, Sidebar, Footer
│   │   ├── charts/             → Chart bar, Chart line (wrapper Chart.js o D3)
│   │   └── magazzino/          → TabellaProdotti, AlertSottoSoglia
│   └── stores/
│       ├── auth.ts             → Auth state (Svelte store)
│       ├── magazzino.ts        → Cache prodotti
│       └── toast.ts            → Notifiche globali
│
└── types/
    └── index.ts                → TypeScript interfaces
```

---

## 5. Implementazione Design System

### 5.1 Tailwind Config (estratto da DESIGN.md)

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        ink: '#000000',
        'canvas-night': '#000000',
        'canvas-night-elevated': '#0a0a0a',
        'canvas-light': '#ffffff',
        'canvas-cream': '#fbfbf5',
        'surface-elevated-dark': '#1e2c31',
        'shade-30': '#d4d4d8',
        'shade-40': '#a1a1aa',
        'shade-50': '#71717a',
        'shade-60': '#52525b',
        'shade-70': '#3f3f46',
        'hairline-light': '#e4e4e7',
        'hairline-dark': '#1e2c31',
        'aloe-10': '#c1fbd4',
        'pistachio-10': '#d4f9e0',
        'link-cool-1': '#9dabad',
        'link-cool-2': '#9797a2',
        'link-cool-3': '#bdbdca',
        'link-mint': '#99b3ad',
      },
      fontFamily: {
        display: ['"Neue Haas Grotesk Display"', 'Helvetica', 'Arial', 'sans-serif'],
        body: ['"Inter Variable"', 'Inter', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'monospace'],
      },
      fontSize: {
        'display-xxl': ['96px', { lineHeight: '1.0', letterSpacing: '2.4px' }],
        'display-xl': ['70px', { lineHeight: '1.0', letterSpacing: '0' }],
        'display-lg': ['55px', { lineHeight: '1.16', letterSpacing: '0' }],
        'display-md': ['48px', { lineHeight: '1.14', letterSpacing: '0' }],
        'heading-xl': ['28px', { lineHeight: '1.28', letterSpacing: '0.42px' }],
        'heading-lg': ['24px', { lineHeight: '1.14', letterSpacing: '0.36px' }],
        'heading-md': ['20px', { lineHeight: '1.4', letterSpacing: '0.3px' }],
        'heading-sm': ['18px', { lineHeight: '1.25', letterSpacing: '0.72px' }],
        'body-lg': ['18px', { lineHeight: '1.56', letterSpacing: '0' }],
        'body-md': ['16px', { lineHeight: '1.5', letterSpacing: '0' }],
        'body-strong': ['16px', { lineHeight: '1.5', letterSpacing: '0' }],
        'caption': ['14px', { lineHeight: '1.49', letterSpacing: '0.28px' }],
        'micro': ['13px', { lineHeight: '1.5', letterSpacing: '-0.13px' }],
        'eyebrow-cap': ['12px', { lineHeight: '1.2', letterSpacing: '0.72px' }],
      },
      borderRadius: {
        'pill': '9999px',
        'xl': '20px',
        'lg': '12px',
        'md': '8px',
        'sm': '5px',
        'xs': '4px',
      },
    }
  }
}
```

### 5.2 Componenti UI Core (da realizzare)

| Componente | Token Design | Note |
|-----------|--------------|------|
| `Button` | `button-primary-pill`, `button-outline-on-dark`, `button-outline-on-light`, `button-aloe-pill` | Shape sempre pill, varianti per canvas |
| `Input` | `text-input` | Bordo hairline-light, rounded-md |
| `Card` | `card-pricing`, `card-pistachio-band`, `card-feature-cinematic` | Varianti light/dark |
| `Badge` | `pill-tag-mint`, `pill-tag-shade` | Per stati ordini, categorie |
| `NavBar` | `nav-bar-light` / `nav-bar-dark` | Switch automatico per pagina |
| `DataTable` | Custom | Tabella prodotti/vendite con sorting, filtri |
| `Toast` | Custom | Notifiche operazioni (verde = successo, rosso = errore) |

### 5.3 Dual Canvas Strategy

L'app adotta la **light track** del design system — essendo un tool transazionale/gestionale:
- Canvas: `canvas-light` / `canvas-cream`
- Testo: `ink`
- Accent: `aloe-10` per azioni primarie, `pistachio-10` per bande di sezione
- Navigazione: `nav-bar-light`
- Cards: `card-pricing` style per le metriche dashboard

La dark track è riservata per eventuali pagine marketing/landing future.

---

## 6. Feature Set Completo

### ✅ Feature Parity (MVP)
- [ ] Upload CSV vendite con preview e conferma
- [ ] Calcolo automatico consumi (vendite × ricette)
- [ ] Visualizzazione magazzino con quantità aggiornate
- [ ] Alert prodotti sotto soglia
- [ ] Download CSV prodotti da riordinare
- [ ] Checklist ricezione ordini con aggiornamento stock
- [ ] Reset dati vendite / magazzino

### 🆕 Nuove Feature (v2)
- [ ] **Auth multi-utente** con ruoli (admin/manager/cuoco)
- [ ] **Multi-ristorante** (team Appwrite separati)
- [ ] **Editor menu visuale** — aggiungi/modifica ricette via form, non solo CSV
- [ ] **Editor magazzino** — CRUD prodotti inline, niente CSV obbligatorio
- [ ] **Storico ordini** — archivio ordini con stati (bozza → inviato → consegnato)
- [ ] **Dashboard analytics** — grafici vendite per periodo, trend consumi, previsioni
- [ ] **Calcolo automatico riordino** — suggerimento quantità basato su consumo medio
- [ ] **Export PDF** — report giornaliero/settimanale
- [ ] **Notifiche push/email** — alert sotto soglia (Appwrite Functions + Webhooks)
- [ ] **Scanner barcode** — (futuro) integrazione camera per check-in prodotti

---

## 7. Flussi Utente

### Flusso 1: Carica Vendite Giornaliere
```
Vendite → Carica CSV
  → Drag & drop file
  → Preview tabella (10 righe)
  → Validazione colonne richieste
  → Conferma → scrive su collection vendite
  → Trigger calcolo consumi automatico
  → Toast "✅ 47 vendite caricate, 12 prodotti aggiornati"
  → Redirect magazzino (vedi sotto soglia)
```

### Flusso 2: Gestione Ordine
```
Magazzino → Riordino
  → Vedi lista prodotti sotto soglia (rosso)
  → Clic "Genera Ordine"
  → Seleziona fornitore per prodotto (o tutti)
  → Crea ordine in stato "bozza"
  → Modifica quantità se necessario
  → "Invia Ordine" → stato "inviato"
  → Scarica CSV ordine per email fornitore

Ordini → [ID Ordine]
  → Carica CSV ricevuto (o modifica manualmente)
  → Checklist prodotti con checkbox
  → "Aggiorna Inventario" → +quantità ricevute
  → Stato → "consegnato"
```

### Flusso 3: Dashboard Analytics
```
Analytics
  → KPI cards (totale vendite oggi, piatti top, prodotti critici)
  → Grafico vendite per giorno (line chart)
  → Grafico consumi per prodotto (bar chart)
  → Tabella prodotti più consumati
  → Filtro per periodo (7g / 30g / custom)
```

---

## 8. Realtime & Ottimizzazioni

### Realtime (Appwrite Subscriptions)
- **Magazzino**: quando un utente aggiorna lo stock, altri utenti vedono il cambiamento live
- **Ordini**: checklist ricezione in tempo reale se più persone collaborano
- **Vendite**: contatore vendite giornaliere si aggiorna in tempo reale

### Caching Strategico (Svelte Stores)
```ts
// Cache locale prodotti per evitare query ripetute
export const prodottiStore = writable<Prodotto[]>([], () => {
  // On first subscriber → fetch from Appwrite
  // On subscribe count 0 → clear after 5min (TTL)
});
```

### CSV Processing Client-Side
- PapaParse per parsing CSV nel browser
- Validazione schema prima dell'upload
- Upload batch su Appwrite (evita timeout)

---

## 9. Deploy su Coolify

### 9.1 Dockerfile (SvelteKit)
```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json .
RUN npm ci --production
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
CMD ["node", "build"]
```

### 9.2 Environment Variables
```bash
# .env (coolify secrets)
PUBLIC_APPWRITE_ENDPOINT=https://appwrite.tuodominio.it/v1
PUBLIC_APPWRITE_PROJECT=xxxxxxxx
APPWRITE_API_KEY=xxxxxxxx  # server-side only
PUBLIC_APPWRITE_DATABASE_ID=inventarify
```

### 9.3 Coolify Setup
1. Nuovo Service → Dockerfile
2. Point al repo Git
3. Environment variables configurate
4. Domains: `inventarify.tuodominio.it`
5. Auto-deploy su push

---

## 10. Roadmap di Implementazione

### Fase 1: Setup & Foundation (Settimana 1)
- [ ] Inizializza progetto SvelteKit + Tailwind + TypeScript
- [ ] Configura Appwrite client, types, constants
- [ ] Implementa design system base (Button, Input, Card, NavBar, Layout)
- [ ] Auth: login/register con Appwrite Auth
- [ ] Middleware protezione route

### Fase 2: Data Layer (Settimana 2)
- [ ] Crea collections Appwrite (prodotti, menu, vendite, ordini, ordini_items)
- [ ] Script Python migrazione dati CSV → Appwrite
- [ ] API layer: CRUD prodotti, menu, vendite, ordini
- [ ] Stores Svelte per caching

### Fase 3: Core Feature — Magazzino & Menu (Settimana 3)
- [ ] Pagina Magazzino: tabella CRUD inline, filtri, ricerca
- [ ] Pagina Menu: editor ricette visuale (aggiungi piatto + ingredienti)
- [ ] Pagina Riordino: prodotti sotto soglia, genera ordine
- [ ] Export CSV riordino

### Fase 4: Vendite & Analytics (Settimana 4)
- [ ] Upload CSV vendite con preview
- [ ] Calcolo consumi automatico post-upload
- [ ] Pagina Analytics: KPI cards, grafici (Chart.js o Tremor)
- [ ] Pagina Vendite: storico con filtri

### Fase 5: Ordini & Polish (Settimana 5)
- [ ] Lista ordini con stati
- [ ] Pagina dettaglio ordine con checklist
- [ ] Aggiornamento magazzino post-ricezione
- [ ] Toast notifications, error handling, loading states
- [ ] Responsive mobile

### Fase 6: Deploy & Beta (Settimana 6)
- [ ] Dockerfile, Coolify deploy
- [ ] SSL, dominio, health checks
- [ ] Test con dati reali
- [ ] Onboarding primo utente ristorante

---

## 11. Costi Stimati (Hetzner + Coolify)

| Servizio | Costo/mese |
|----------|-----------|
| Hetzner CPX21 (4 vCPU, 8GB RAM) | ~€12 |
| Appwrite (self-hosted) | €0 |
| Coolify | €0 (open source) |
| Dominio | ~€10/anno |
| **Totale** | **~€12/mese** |

Appwrite self-hosted su Hetzner gestisce tranquillamente 1-5 ristoranti. Se in futuro cresci, puoi scalare il server o passare ad Appwrite Cloud.

---

## 12. File di Avvio Rapido

```bash
# 1. Clona repo e crea progetto
npx sv create inventarify-frontend  # SvelteKit skeleton

# 2. Installa dipendenze
cd inventarify-frontend
npm install -D tailwindcss postcss autoprefixer
npm install appwrite chart.js papaparse @types/papaparse

# 3. Configura Tailwind + design tokens
npx tailwindcss init -p

# 4. Avvia dev server
npm run dev
```

---

## Riepilogo Decisioni Architetturali

| Decisione | Scelta | Perché |
|-----------|--------|--------|
| Frontend | SvelteKit | Leggero, veloce, perfetto per tool interni |
| Backend | Appwrite self-hosted | Zero codice backend, auth/db/storage pronti |
| Styling | Tailwind + token | Fedele a DESIGN.md, manutenibile |
| Deploy | Coolify + Hetzner | Già presente, costi bassi, pieno controllo |
| DB | Appwrite Document Store | Native JSON, relazioni, realtime integrato |
| Mobile | Responsive PWA | Una sola codebase, funziona su tablet in cucina |

---

**Prossimo step**: vuoi che inizi con il setup del progetto SvelteKit + Tailwind + Appwrite client? Oppure preferisci partire dalla configurazione delle collections Appwrite?
