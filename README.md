# NormaPy

NormaPy is a web platform for importing, normalizing, and managing product catalogs from CSV/Excel files. It features smart column mapping, robust heuristics, and manual mapping adjustment.

## Features

- Import CSV/Excel files through a user-friendly web interface.
- Automatic column mapping using configurable synonyms and smart heuristics.
- Manual mapping adjustment: users can select which file column matches each internal field before confirming the import.
- Preview of normalized data before saving.
- Import history and product management.
- Pure Django backend, no React frontend dependencies.

## Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/pipjoy/NormaPy.git
cd NormaPy
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

### 6. Access the platform

Open your browser at [http://127.0.0.1:8000/importar/](http://127.0.0.1:8000/importar/)

---

## Import Workflow

1. Click "Import products" to go to the import page.
2. Upload your CSV or Excel file.
3. The system will:
   - Normalize column names.
   - Match them against `sinonimos.json`.
   - Apply heuristics if needed.
   - Show the editable mapping and a data preview.
4. Adjust the mapping manually if needed.
5. Confirm the import to save products to the database.

---

## Customizing the Mapping

- Edit `normapy/mapeo/sinonimos.json` to add column aliases according to your real files.
- Improve heuristics in `normapy/mapeo/heuristicas.py` if you have special patterns.

---

## Relevant Structure

- `normapy/mapeo/sinonimos.json` — Column synonyms.
- `normapy/mapeo/heuristicas.py` — Heuristics for automatic detection.
- `normapy/mapeo/normalizador.py` — Normalization and mapping logic.
- `normapy/templates/normapy/importar.html` — Import and mapping editing interface.

---

## License

MIT

---

Questions, suggestions, or improvements? Open an issue or pull request!