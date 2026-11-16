import pytest


@pytest.fixture(autouse=True)
def fake_aws_credentials(monkeypatch):
    monkeypatch.setenv("S3_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("S3_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("S3_REGION", "eu-west-3")