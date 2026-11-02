from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import io

import requests


API_URL = "https://eeadmz1-downloads-api-appservice.azurewebsites.net/ParquetFile/dynamic"

OUTPUT_DIR = Path("data/eea_recent")
ZIP_PATH = OUTPUT_DIR / "eea_recent.zip"
EXTRACT_DIR = OUTPUT_DIR / "extracted"

# Période récente : les 7 derniers jours
now = datetime.now(timezone.utc)
start = now - timedelta(days=7)

payload = {
    "countries": ["FR"],
    "cities": [],
    "pollutants": ["PM2.5"],
    "dataset": 1,  # E2a : données Up-To-Date non vérifiées
    "dateTimeStart": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "dateTimeEnd": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "aggregationType": "hour",
    "source": "API",
    "method": "dynamic",
    "compress": True,
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Période demandée : {start.isoformat()} -> {now.isoformat()}")
print("Téléchargement des données EEA...")

response = requests.post(API_URL, json=payload, timeout=300)

if response.status_code not in (200, 206):
    print(f"Erreur HTTP : {response.status_code}")
    print(response.text[:1000])
    response.raise_for_status()

if not response.content:
    raise RuntimeError("La réponse de l'API est vide.")

# Enregistrer l'archive originale
ZIP_PATH.write_bytes(response.content)
print(f"Archive enregistrée : {ZIP_PATH}")
print(f"Taille : {ZIP_PATH.stat().st_size / 1024:.1f} Ko")

# Vérifier et extraire le ZIP
try:
    with ZipFile(io.BytesIO(response.content)) as archive:
        print("\nContenu de l'archive :")
        for item in archive.infolist():
            print(f"  {item.filename} ({item.file_size / 1024:.1f} Ko)")

        archive.extractall(EXTRACT_DIR)

except BadZipFile as exc:
    raise RuntimeError(
        "La réponse n'est pas une archive ZIP valide. "
        "Vérifie le contenu et le statut HTTP."
    ) from exc

print(f"\nFichiers extraits dans : {EXTRACT_DIR}")

# Rechercher tous les fichiers Parquet extraits
parquet_files = list(EXTRACT_DIR.rglob("*.parquet"))

if not parquet_files:
    print("Aucun fichier Parquet trouvé.")
    raise SystemExit(0)

print(f"\nNombre de fichiers Parquet : {len(parquet_files)}")

print("\nInspection terminée.")