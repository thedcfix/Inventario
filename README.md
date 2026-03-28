# Inventario

Applicazione web di gestione inventario costruita con Flask. Permette di creare, visualizzare, modificare ed eliminare articoli, gestire foto, organizzare per categorie, cercare/filtrare ed esportare i dati in Excel.

## Funzionalità

- **CRUD articoli**: creazione, visualizzazione, modifica ed eliminazione di articoli con nome, descrizione, categoria, quantità, prezzo e foto
- **Gestione foto**: upload e cattura da fotocamera con compressione automatica lato client (max 1200×1200px, JPEG 80%)
- **Categorie dinamiche**: selezione da categorie esistenti o creazione al volo di nuove categorie
- **Ricerca e filtro**: ricerca per nome/descrizione e filtro per categoria
- **Esportazione Excel**: download di un file `.xlsx` formattato con tutti gli articoli e calcolo del valore totale
- **Autenticazione**: login con username e password (hash bcrypt), protezione di tutte le rotte tramite decoratore `@login_required`
- **Dual-mode**: funziona con Azure Cosmos DB + Blob Storage in produzione oppure con file JSON locale + filesystem in sviluppo

## Struttura del progetto

```
app.py                  # Applicazione Flask: rotte, autenticazione, logica principale
config.py               # Configurazione da variabili d'ambiente
Procfile                # Deploy cloud (gunicorn)
startup.sh              # Avvio locale (gunicorn su porta 8000)
requirements.txt        # Dipendenze Python
data/
  items.json            # Database locale (fallback JSON)
services/
  cosmos_service.py     # Servizio Azure Cosmos DB
  local_service.py      # Servizio locale (JSON + filesystem)
  storage_service.py    # Servizio Azure Blob Storage
static/
  css/style.css         # Stili custom (CSS variables, responsive)
  js/camera.js          # Gestione upload foto e compressione immagini
  uploads/              # Foto salvate in locale
  vendor/               # Bootstrap 5.3, Bootstrap Icons, font Inter
templates/
  base.html             # Layout base (navbar, gestione errori)
  login.html            # Pagina di login
  index.html            # Dashboard con griglia articoli
  item_form.html        # Form creazione/modifica articolo
  item_detail.html      # Dettaglio singolo articolo
```

## Rotte

| Rotta | Metodo | Descrizione |
|-------|--------|-------------|
| `/login` | GET, POST | Pagina di autenticazione |
| `/logout` | GET | Disconnessione e redirect al login |
| `/` | GET | Dashboard: griglia articoli con ricerca e filtro |
| `/api/items` | GET | API JSON per ricerca asincrona |
| `/export` | GET | Download Excel dell'inventario |
| `/item/new` | GET, POST | Creazione nuovo articolo |
| `/item/<id>` | GET | Dettaglio articolo |
| `/item/<id>/edit` | GET, POST | Modifica articolo |
| `/item/<id>/delete` | POST | Eliminazione articolo |

## Modello dati

Ogni articolo ha la seguente struttura:

| Campo | Tipo | Note |
|-------|------|------|
| `id` | string (UUID) | Generato automaticamente |
| `name` | string | Obbligatorio, max 200 caratteri |
| `description` | string | Opzionale, max 2000 caratteri |
| `category` | string | Obbligatorio |
| `quantity` | integer | Default 1 |
| `price` | float | Default 0 |
| `photo_url` | string | URL foto o vuoto |
| `blob_name` | string | Riferimento blob storage (opzionale) |
| `created_at` | string | Timestamp ISO 8601 UTC |
| `updated_at` | string | Timestamp ISO 8601 UTC |

## Servizi

L'applicazione sceglie automaticamente il backend in base alla presenza delle credenziali Azure:

- **CosmosService** (`cosmos_service.py`): operazioni CRUD su Azure Cosmos DB con query SQL-like, ricerca full-text e lettura per partizione
- **StorageService** (`storage_service.py`): upload/download/eliminazione foto su Azure Blob Storage con URL SAS
- **LocalCosmosService / LocalStorageService** (`local_service.py`): fallback locale che salva i dati in `data/items.json` e le foto in `static/uploads/`

## Configurazione

Variabili d'ambiente (caricabili da file `.env`):

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `SECRET_KEY` | `"change-me-in-production"` | Chiave di cifratura sessioni Flask |
| `APP_USERNAME` | `"admin"` | Username di login |
| `APP_PASSWORD_HASH` | — | Hash bcrypt della password (obbligatorio) |
| `COSMOS_ENDPOINT` | — | Endpoint Azure Cosmos DB |
| `COSMOS_KEY` | — | Chiave primaria Cosmos DB |
| `COSMOS_DATABASE` | `"inventario"` | Nome database |
| `COSMOS_CONTAINER` | `"items"` | Nome container |
| `AZURE_STORAGE_CONNECTION_STRING` | — | Stringa di connessione Blob Storage |
| `AZURE_STORAGE_CONTAINER` | `"photos"` | Nome container blob |

Per generare l'hash della password:

```bash
flask generate-hash
```

## Dipendenze

- **Flask 3.1** — framework web
- **python-dotenv 1.1** — caricamento `.env`
- **azure-cosmos 4.9** — client Cosmos DB
- **azure-storage-blob 12.25** — client Blob Storage
- **gunicorn 23.0** — server WSGI di produzione
- **openpyxl 3.1** — generazione file Excel
- **Werkzeug 3.1** — utilità WSGI e hashing password

## Avvio

**Sviluppo locale:**

```bash
pip install -r requirements.txt
flask run
```

**Produzione (gunicorn):**

```bash
./startup.sh
```

Il server si avvia su `http://localhost:8000` con 2 worker e 4 thread per worker.

## Interfaccia

- **Framework UI**: Bootstrap 5.3 con Bootstrap Icons
- **Font**: Inter (Google Fonts)
- **Tema**: colore primario indaco (`#4f46e5`), effetto glassmorphism sulla navbar, design responsive mobile-first
- **Lingua**: italiano
