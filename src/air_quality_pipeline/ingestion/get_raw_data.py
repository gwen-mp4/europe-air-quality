import requests
import pandas as pd
from pathlib import Path
from zipfile import ZipFile

url = "https://eeadmz1-downloads-api-appservice.azurewebsites.net/"
endpoint = "ParquetFile"

payload = {
    "countries": ["FR"],
    "cities": [],
    "pollutants": ["PM2.5"],
    "dataset": 2,
    "dateTimeStart": "2024-01-01T00:00:00Z",
    "dateTimeEnd": "2024-01-07T23:59:59Z",
    "aggregationType": "hour",
}


res = requests.post(f"{url}{endpoint}",
                   json=payload,
                   timeout=120,
)

res.raise_for_status()
zip_path = Path("data/eea_sample.zip")
extract_dir = Path("data/extracted")

extract_dir.parent.mkdir(parents=True, exist_ok=True)

with ZipFile(zip_path, "r") as archive:
    archive.extractall(extract_dir)

print("Fichiers extraits :")
for path in extract_dir.rglob("*"):
    if path.is_file():
        print(path)

files = list(Path("data/extracted").rglob("*.parquet"))

if not files:
    print("Aucun fichier Parquet trouvé.")
else:
    df = pd.read_parquet(files[0])

    print(df.head(10))
    print(df.shape)
    print(df.columns.tolist())
    print(df.dtypes)