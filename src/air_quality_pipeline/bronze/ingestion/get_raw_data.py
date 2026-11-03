from datetime import date
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZipFile, is_zipfile
import logging

import boto3
import requests
from botocore.exceptions import ClientError

from air_quality_pipeline.bronze.ingestion.get_date import generate_months_period
from air_quality_pipeline.bronze.utils import (
    setup_logging,
    URL,
    ENDPOINT,
    BUCKET,
    ARCHIVES_PREFIX,
    PARQUET_PREFIX,
    COUNTRIES,
    POLLUTANTS,
    START_YEAR,
    START_MONTH,
    END_YEAR,
    END_MONTH,
)

logger = logging.getLogger(__name__)

s3 = boto3.client("s3")


def key_exists(key: str) -> bool:
    """Return True if S3 object exists."""

    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def fetch_archive(
        payload: dict,
        archive_name: str,
) -> bytes:
   """Download an EEA ZIP archive and return its content."""

   res = requests.post(f"{URL}{ENDPOINT}", json=payload, timeout=120)
   res.raise_for_status()

   if not is_zipfile(BytesIO(res.content)):
       raise ValueError(f"The EEA response is not a valid ZIP: {archive_name}")

   logger.debug("Data retrieved: %s", archive_name)
   return res.content


def extract_zip_to_s3(
        content: bytes,
        parquet_prefix: str,
) -> None:
    """Upload each file of the ZIP to S3, then write a _SUCCESS marker."""

    logger.debug("Checking before extracting: %s", parquet_prefix)
    with ZipFile(BytesIO(content)) as archive:
        # Prevent file in the archive from escaping the destination
        for member in archive.infolist():
            if member.is_dir():
                logger.warning("Directory in %s, skipping", parquet_prefix)
                continue

            parts = PurePosixPath(member.filename).parts
            if ".." in parts or member.filename.startswith("/"):
                raise ValueError(f"Unsafe path in archive: {member.filename}")

            logger.debug("Extracting: %s", parquet_prefix)
            with archive.open(member) as f:
                s3.upload_fileobj(f, BUCKET, f"{parquet_prefix}/{member.filename}")

    # Creating an empty _SUCCESS file to avoid repeating the same process
    logger.debug("Creating _SUCCESS file: %s", parquet_prefix)
    s3.put_object(Bucket=BUCKET, Key=f"{parquet_prefix}/_SUCCESS", Body=b"")
    logger.info("Extracted to s3://%s/%s", BUCKET, parquet_prefix)


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

    pollutant_norm = pollutant.replace(".", "")
    start = date.fromisoformat(date_start)

    archive_name = f"eea_{country}_{pollutant_norm}_{date_start}_{date_end}.zip"
    archive_key = f"{ARCHIVES_PREFIX}/{archive_name}"
    parquet_prefix = (
        f"{PARQUET_PREFIX}/country={country}/pollutant_name={pollutant_norm}"
        f"/year={start.year}/month={start.month:02d}"
    )

    logger.debug("Downloading: %s", archive_name)

    if key_exists(f"{parquet_prefix}/_SUCCESS"):
        logger.warning("Already processed: %s", archive_name)
        return

    if key_exists(archive_key):
        logger.warning("Archive already in S3: %s", archive_name)
        content = s3.get_object(Bucket=BUCKET, Key=archive_key)["Body"].read()
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

        logger.debug("Fetching archive with payload: %s", payload)
        content = fetch_archive(payload, archive_name)
        s3.put_object(Bucket=BUCKET, Key=archive_key, Body=content)
        logger.info("Uploaded: s3://%s/%s", BUCKET, archive_key)

    extract_zip_to_s3(content, parquet_prefix)


if __name__ == "__main__":
    setup_logging()
    for country in COUNTRIES:
        for pollutant in POLLUTANTS:
            for start_date, end_date in generate_months_period(
                    f"{START_YEAR}-{START_MONTH:02d}-01",
                    f"{END_YEAR}-{END_MONTH:02d}-01",
            ):
                download_from_src(
                    country=country,
                    pollutant=pollutant,
                    date_start=start_date,
                    date_end=end_date,
                )