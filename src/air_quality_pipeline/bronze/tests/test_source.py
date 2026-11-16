import io
import zipfile
from unittest.mock import Mock

import boto3
import pytest
from moto import mock_aws

from src.air_quality_pipeline.bronze.ingestion import (
    generate_months_period,
    get_raw_data,
)


@pytest.mark.parametrize(
    "start, end",
    [
        ("04/01/2022", "04/02/2022"),
        ("2023/03/01", "2023/04/01"),
        ("2023-02-29", "2023-03-01"),
        ("2024-02-30", "2024-03-01"),
        ("not a date", "2024-01-01"),
        ("2024-13-01", "2024-13-31"),
        ("2024-00-01", "2024-00-31"),
        ("2024-01-00", "2024-01-31"),
        ("2024-01-32", "2024-01-31"),
        ("2024-01-01", "2023-12-31"),
        ("556-01-01", "556-02-01"),
    ],
)
def test_generate_months_period_rejects_invalid_dates(start, end):
    with pytest.raises(ValueError):
        list(generate_months_period(start, end))


def test_generate_months_period_accepts_zero_padded_year():
    assert list(generate_months_period("0556-01-01", "0556-02-01")) == [
        ("0556-01-01", "0556-01-31"),
        ("0556-02-01", "0556-02-29"),
    ]


def make_zip(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return buffer.getvalue()


@pytest.fixture
def s3_bucket(monkeypatch):
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-3")
        s3.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
        )
        monkeypatch.setattr(get_raw_data, "s3", s3)
        monkeypatch.setattr(get_raw_data, "BUCKET", "test-bucket")
        yield s3


def test_extraction_uploads_each_file(s3_bucket):
    content = make_zip({"a.parquet": b"x", "b.parquet": b"y"})
    get_raw_data.extract_zip_to_s3(content, "raw/eea/parquet/test", False, None)
    keys = {o["Key"] for o in s3_bucket.list_objects_v2(Bucket="test-bucket")["Contents"]}
    assert "raw/eea/parquet/test/a.parquet" in keys
    assert "raw/eea/parquet/test/b.parquet" in keys


def test_unsafe_path_is_rejected_and_nothing_is_uploaded(s3_bucket):
    content = make_zip({"../evil.parquet": b"x"})
    with pytest.raises(ValueError):
        get_raw_data.extract_zip_to_s3(content, "raw/eea/parquet/test", True, None)
    assert "Contents" not in s3_bucket.list_objects_v2(Bucket="test-bucket")


def test_non_zip_response_is_rejected(monkeypatch):
    fake = Mock(content=b"not a zip")
    fake.raise_for_status.return_value = None
    monkeypatch.setattr(get_raw_data.requests, "post", lambda *a, **k: fake)
    with pytest.raises(ValueError):
        get_raw_data.fetch_archive({"countries": ["FR"]}, "x.zip")