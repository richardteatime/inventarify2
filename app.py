import streamlit as st
import pandas as pd
import duckdb
import sqlite3
import os
import altair as alt

st.set_page_config(page_title="Inventario Ristorante", layout="wide")

# Percorsi database
DB_PATH = "inventario.db"

# Creazione DB se non esiste
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    pd.read_csv("prodotti_magazzino.csv").to_sql("prodotti_magazzino", conn, if_exists="replace", index=False)
    pd.read_csv("menu.csv").to_sql("menu", conn, if_exists="replace", index=False)
    conn.close()

# Connessione DuckDB via SQLite
con = duckdb.connect()
con.execute(f"INSTALL sqlite; LOAD sqlite;")
con.execute(f"ATTACH DATABASE '{DB_PATH}' AS db;")

# Funzione di refresh
@st.experimental_fragment
def refresh_data():
    st.session_state["_rerun_trigger"] = not st.session_state.get("_rerun_trigger", False)

# Sidebar con navigazione
st.sidebar.title("📂 Menu Navigazione")
section = st.sidebar.radio("Vai a:", ["🏠 Home", "📊 Analytics", "📦 Prodotti Magazzino", "🍽️ Menu", "🧾 Vendite", "📋 Ordini"])

# Upload vendite sempre visibile
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Carica Vendite")
uploaded_vendite = st.sidebar.file_uploader("Carica vendite.csv", type=["csv"])

if uploaded_vendite:
    df_vendite_new = pd.read_csv(uploaded_vendite)
    conn = sqlite3.connect(DB_PATH)
    try:
        df_existing = pd.read_sql("SELECT * FROM vendite", conn)
        df_combined = pd.concat([df_existing, df_vendite_new], ignore_index=True)
        df_combined.drop_duplicates(subset=["data", "piatto"], keep="last", inplace=True)
    except Exception:
        df_combined = df_vendite_new
    df_combined.to_sql("vendite", conn, if_exists="replace", index=False)
    conn.close()
    st.sidebar.success("✅ Vendite aggiunte al database")
    st.session_state["_rerun_trigger"] = not st.session_state.get("_rerun_trigger", False)

# Pulsante reset vendite
if section == "🧾 Vendite":
    if st.button("🗑️ Reset Vendite"):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vendite")
            conn.commit()
            conn.close()
            st.success("✅ Tutte le vendite sono state eliminate.")
            st.session_state["_rerun_trigger"] = not st.session_state.get("_rerun_trigger", False)
        except Exception as e:
            st.error(f"❌ Errore durante l'eliminazione delle vendite: {e}")

# Pulsante reset magazzino
if section == "📦 Prodotti Magazzino":
    if st.button("🗑️ Reset Magazzino"):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prodotti_magazzino")
            conn.commit()
            conn.close()
            st.success("✅ Tutti i dati del magazzino sono stati eliminati.")
            st.session_state["_rerun_trigger"] = not st.session_state.get("_rerun_trigger", False)
        except Exception as e:
            st.error(f"❌ Errore durante l'eliminazione del magazzino: {e}")

# HOME
if section == "🏠 Home":
    st.title("🍽️ Sistema Intelligente di Gestione Magazzino")

    st.markdown("""
    Benvenuto nella piattaforma di **gestione magazzino intelligente** per ristoranti!

    Questo software ti permette di automatizzare e tenere sotto controllo in tempo reale le attività legate all'inventario, alle vendite e agli ordini di approvvigionamento.
    """)

    st.markdown("""
    ### 🔧 Funzionalità principali
    - **Carica le vendite giornaliere** da file `.csv`
    - **Visualizza i consumi** degli ingredienti derivanti dalle vendite
    - **Controlla il magazzino** e ricevi segnalazioni automatiche dei prodotti sotto scorta
    - **Scarica la lista degli articoli da riordinare** in formato `.csv`
    - **Carica gli ordini ricevuti** e aggiorna le quantità tramite una checklist interattiva
    - **Analizza dati e trend** con grafici e riepiloghi
    """)

    st.markdown("""
    ### 🧠 Flusso logico del sistema
    
    #### 1. Inserimento dati:
    - Carica **menu.csv** (ricette) e **prodotti_magazzino.csv** (scorte iniziali)
    - Carica **vendite.csv** giornalmente dalla sidebar

    #### 2. Calcolo consumi:
    - Il sistema calcola i consumi automatici incrociando vendite e ricette
    - Vengono aggiornate le quantità residue in magazzino

    #### 3. Riordino:
    - Se un prodotto scende sotto soglia, viene segnalato
    - È possibile scaricare un file `.csv` per l'ordine da inviare al fornitore

    #### 4. Ricezione merce:
    - Carica il file ricevuto con le quantità
    - Usa la checklist per confermare gli articoli arrivati
    - Il magazzino si aggiorna automaticamente
    """)

    st.markdown("""
    ### 📌 Requisiti file CSV
    - `menu.csv`: `piatto`, `prodotto`, `quantità_prodotto`
    - `prodotti_magazzino.csv`: `prodotto`, `quantità_attuale`, `unità`, `soglia_riordino`
    - `vendite.csv`: `data`, `piatto`, `quantità_venduta`
    - `ordini.csv`: `prodotto`, `quantità`
    """)

    st.markdown("""
    ---
    ⚠️ Tutti i file devono rispettare la struttura specificata per evitare errori nel sistema.
    Utilizza i pulsanti di reset nelle sezioni **Vendite** e **Magazzino** per ripartire da zero in fase di test o aggiornamento massivo.
    """)

# ANALYTICS
elif section == "📊 Analytics":
    st.title("📈 Reportistica e Analisi")
    st.markdown("### 🔍 Panoramica delle vendite e dell'inventario")

    try:
        vendite_df = con.execute("SELECT * FROM db.vendite").fetchdf()
    except Exception:
        st.warning("⚠️ Nessuna vendita disponibile nel database. Carica un file nella sidebar.")
        vendite_df = pd.DataFrame(columns=["data", "piatto", "quantità_venduta"])

    menu_df = con.execute("SELECT * FROM db.menu").fetchdf()
    total_sales = vendite_df["quantità_venduta"].sum()
    unique_dishes = vendite_df["piatto"].nunique()
    most_sold = vendite_df.groupby("piatto")["quantità_venduta"].sum().sort_values(ascending=False).reset_index()
    top_dish = most_sold.iloc[0] if not most_sold.empty else {"piatto": "N/A", "quantità_venduta": 0}

    col1, col2, col3 = st.columns(3)
    col1.metric("🍽️ Totale Piatti Venduti", total_sales)
    col2.metric("📋 Piatti Diversi Venduti", unique_dishes)
    col3.metric("🏆 Piatto più venduto", f"{top_dish['piatto']} ({top_dish['quantità_venduta']})")

    # Tabelle piatti più ordinati e consumo
    consumo_df = vendite_df.merge(menu_df, on="piatto")
    consumo_df["consumo_totale"] = consumo_df["quantità_venduta"] * consumo_df["quantità_prodotto"]
    consumo_totale_df = consumo_df.groupby("prodotto")["consumo_totale"].sum().reset_index()

    st.markdown("### 📋 Tabelle Analitiche")
    t1, t2 = st.columns(2)
    with t1:
        st.subheader("📌 Piatti più Ordinati")
        st.dataframe(most_sold, height=300)
    with t2:
        st.subheader("🔎 Consumo Ingredienti")
        st.dataframe(consumo_totale_df, height=300)

    # Grafico consumo
    st.markdown("### 📊 Visualizzazioni")
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("🍅 Ingredienti più Utilizzati")
        chart = alt.Chart(consumo_totale_df).mark_bar(color='#1f77b4').encode(
            x=alt.X("prodotto", sort="-y"),
            y="consumo_totale",
            tooltip=["prodotto", "consumo_totale"]
        ).properties(width=350, height=300)
        st.altair_chart(chart, use_container_width=True)
    with g2:
        st.subheader("🍽️ Piatti più Ordinati")
        chart_dishes = alt.Chart(most_sold).mark_bar(color='#ff7f0e').encode(
            x=alt.X("piatto", sort="-y"),
            y="quantità_venduta",
            tooltip=["piatto", "quantità_venduta"]
        ).properties(width=350, height=300)
        st.altair_chart(chart_dishes, use_container_width=True)

    # Grafico prodotti sotto soglia
    st.markdown("### 🚨 Prodotti da Riordinare")
    try:
        inventario_df = con.execute("SELECT * FROM db.prodotti_magazzino").fetchdf()
        consumo_df = vendite_df.merge(menu_df, on="piatto")
        consumo_df["consumo_totale"] = consumo_df["quantità_venduta"] * consumo_df["quantità_prodotto"]
        consumo_totale_df = consumo_df.groupby("prodotto")["consumo_totale"].sum().reset_index()
        inventario_df = inventario_df.merge(consumo_totale_df, on="prodotto", how="left").fillna(0)
        inventario_df["quantità_aggiornata"] = inventario_df["quantità_attuale"] - inventario_df["consumo_totale"]
        inventario_df["sotto_soglia"] = inventario_df["quantità_aggiornata"] < inventario_df["soglia_riordino"]
        sotto_df = inventario_df[inventario_df["sotto_soglia"] == True]
        if not sotto_df.empty:
            soglia_chart = alt.Chart(sotto_df).mark_bar(color='#d62728').encode(
                x=alt.X("prodotto", sort="-y"),
                y="quantità_aggiornata",
                tooltip=["prodotto", "quantità_aggiornata", "soglia_riordino"]
            ).properties(width=800)
            st.altair_chart(soglia_chart, use_container_width=True)
        else:
            st.success("✅ Nessun prodotto sotto soglia.")
    except Exception:
        st.info("ℹ️ Nessun dato disponibile per i prodotti da riordinare.")
    

# MAGAZZINO
elif section == "📦 Prodotti Magazzino":
    st.title("📦 Inventario Magazzino")

    st.subheader("📤 Aggiorna Inventario da CSV")
    upload_inv = st.file_uploader("Carica nuovo prodotti_magazzino.csv", type=["csv"], key="upload_inv")
    if upload_inv:
        df_new_inv = pd.read_csv(upload_inv)
        df_new_inv.to_sql("prodotti_magazzino", sqlite3.connect(DB_PATH), if_exists="replace", index=False)
        st.success("✅ Inventario aggiornato!")
        st.session_state["_rerun_trigger"] = not st.session_state.get("_rerun_trigger", False)

    try:
        magazzino_df = con.execute("SELECT * FROM db.prodotti_magazzino").fetchdf()
    except Exception:
        st.warning("⚠️ Nessun inventario disponibile nel database. Carica un file nella sezione sottostante.")
        magazzino_df = pd.DataFrame(columns=["prodotto", "quantità_attuale", "unità", "soglia_riordino"])

    try:
        vendite_df = con.execute("SELECT * FROM db.vendite").fetchdf()
    except Exception:
        st.warning("⚠️ Nessuna vendita disponibile nel database. Carica un file nella sidebar.")
        vendite_df = pd.DataFrame(columns=["data", "piatto", "quantità_venduta"])

    menu_df = con.execute("SELECT * FROM db.menu").fetchdf()

    # Calcolo consumo
    consumo_df = vendite_df.merge(menu_df, on="piatto")
    consumo_df["consumo_totale"] = consumo_df["quantità_venduta"] * consumo_df["quantità_prodotto"]
    consumo_totale_df = consumo_df.groupby("prodotto")["consumo_totale"].sum().reset_index()

    inventario_df = magazzino_df.merge(consumo_totale_df, on="prodotto", how="left").fillna(0)
    inventario_df["quantità_aggiornata"] = inventario_df["quantità_attuale"] - inventario_df["consumo_totale"]
    inventario_df["sotto_soglia"] = inventario_df["quantità_aggiornata"] < inventario_df["soglia_riordino"]

    st.dataframe(inventario_df[["prodotto", "quantità_aggiornata", "unità", "soglia_riordino", "sotto_soglia"]])

    # MAGAZZINO — download aggiornato
    if inventario_df["sotto_soglia"].any():
        st.warning("⚠️ Alcuni prodotti sono sotto la soglia di riordino!")

        sotto_df = inventario_df[inventario_df["sotto_soglia"] == True].copy()
        sotto_df["quantità"] = sotto_df["soglia_riordino"] - sotto_df["quantità_aggiornata"]
        sotto_df["quantità"] = sotto_df["quantità"].clip(lower=1).round().astype(int)
        sotto_df["sotto_soglia"] = False
        export_df = sotto_df[["prodotto", "quantità"]]
        csv = export_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Scarica Prodotti da Riordinare",
            data=csv,
            file_name="prodotti_da_riordinare.csv",
            mime="text/csv"
        )

# MENU
elif section == "🍽️ Menu":
    st.title("🍽️ Menu - Ricette Piatti")

    menu_df = con.execute("SELECT * FROM db.menu").fetchdf()
    st.dataframe(menu_df)

    st.subheader("📤 Aggiorna Menu da CSV")
    upload_menu = st.file_uploader("Carica nuovo menu.csv", type=["csv"], key="upload_menu")
    

# VENDITE
elif section == "🧾 Vendite":
    st.title("🧾 Storico Vendite Caricate")
    try:
        vendite_df = con.execute("SELECT * FROM db.vendite").fetchdf()
        st.dataframe(vendite_df)
    except Exception:
        st.info("📭 Nessuna vendita registrata nel sistema.")
    
# ORDINI
elif section == "📋 Ordini":
    st.title("📋 Gestione Ordini")
    st.markdown("Carica un file CSV con i prodotti ordinati e usa la checklist per tenere traccia della ricezione.")

    uploaded_orders = st.file_uploader("Carica ordini.csv", type=["csv"], key="upload_orders")

    if uploaded_orders:
        df_ordini = pd.read_csv(uploaded_orders)

        if "quantità" not in df_ordini.columns and "quantità_aggiornata" in df_ordini.columns:
            df_ordini.rename(columns={"quantità_aggiornata": "quantità"}, inplace=True)

        if "prodotto" in df_ordini.columns and "quantità" in df_ordini.columns:
            st.success("✅ File caricato correttamente!")
            st.markdown("### 🧾 Checklist Ordini Ricevuti")
            checklist_data = []
            for i, row in df_ordini.iterrows():
                key = f"check_{i}_{row['prodotto']}"
                checked = st.checkbox(f"✅ {row['prodotto']} — {row['quantità']} unità", key=key)
                checklist_data.append({"prodotto": row["prodotto"], "quantità": row["quantità"], "ricevuto": checked})

            st.markdown("---")
            st.markdown("### 📋 Riepilogo Stato Ordini")
            df_checklist = pd.DataFrame(checklist_data)
            st.dataframe(df_checklist)

            if st.button("📦 Aggiorna Inventario"):
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    for _, row in df_checklist[df_checklist["ricevuto"] == True].iterrows():
                        cursor.execute(
                            """
                            UPDATE prodotti_magazzino
                            SET quantità_attuale = quantità_attuale + ?
                            WHERE prodotto = ?
                            """,
                            (int(row["quantità"]), row["prodotto"])
                        )
                    conn.commit()
                    conn.close()
                    st.success("✅ Inventario aggiornato con successo!")
                    st.session_state["_rerun_trigger"] = not st.session_state.get("_rerun_trigger", False)
                except Exception as e:
                    st.error(f"❌ Errore durante l'aggiornamento: {e}")
        else:
            st.error("❌ Il file deve contenere le colonne 'prodotto' e 'quantità'.")
