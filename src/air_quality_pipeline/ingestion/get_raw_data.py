import requests
import pandas as pd
from pathlib import Path
from zipfile import ZipFile, is_zipfile
from io import BytesIO
import logging


logging.basicConfig(
	level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


URL = "https://eeadmz1-downloads-api-appservice.azurewebsites.net/"
ENDPOINT = "ParquetFile"

RAW_DIR = Path("data/raw/eea")
ARCHIVES_DIR = RAW_DIR / "archives"
PARQUET_DIR = RAW_DIR / "parquet"


# Add variable validation later (e.g. pollutant must be PM2.5, PM10, CO etc...)
# Add try-expect too
def download_from_src(
        country: str,
        pollutant: str,
        date_start: str,
        date_end: str,
        dataset: int = 2,
        agg_type: str = "hour"
) -> None:
    """Download an EEA ZIP archive."""

    pollutant_norm = pollutant.replace(".", "")
    archive_name = (
        f"eea_{country}_{pollutant_norm}_"
        f"{date_start}_{date_end}.zip"
    )

    archive_path = ARCHIVES_DIR / archive_name

    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)

    if archive_path.exists() and is_zipfile(archive_path):
        logging.warning(f"Archive already downloaded: {archive_name}")
    else:
        payload = {
            "countries": [country],
            "cities": [],
            "pollutants": [pollutant],
            "dataset": dataset,
            "dateTimeStart": f"{date_start}T00:00:00Z",
            "dateTimeEnd": f"{date_end}T23:59:59Z",
            "aggregationType": agg_type,
        }

        res = requests.post(
            f"{URL}{ENDPOINT}",
            json=payload,
            timeout=120,
        )
        res.raise_for_status()

        if not is_zipfile(BytesIO(res.content)):
            raise ValueError(
                f"The EEA response is not a valid ZIP: {archive_name}"
            )

        archive_path.write_bytes(res.content)
        logging.info(f"Downloaded: {archive_path}")

    # Extract ZIP file
    try:
        extract_zip(archive_path)
    except Exception as e:
        logging.error(f"Failed to extract ZIP: {e}")


def extract_zip(
        archive_path: str,
) -> None:
    """Extract ZIP from the archive path."""

    extract_dir = PARQUET_DIR / archive_path.stem

    PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    if extract_dir.exists() and any(extract_dir.iterdir()):
        logging.warning(f"ZIP already extracted: {extract_dir}")
        return

    extract_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(archive_path, "r") as archive:
        # Prevent file in the archive from escaping the destination
        for member in archive.infolist():
            dest = (extract_dir / member.filename).resolve()

            if not dest.is_relative_to(extract_dir.resolve()):
                raise ValueError(
                    f"Unsafe path in archive: {member.filename}"
                )

            archive.extractall(extract_dir)
            logging.info(f"Extracted: {archive_path}")


if __name__ == "__main__":
    download_from_src(
        country="FR",
        pollutant="PM2.5",
        date_start="2024-01-01",
        date_end="2024-01-07",
    )