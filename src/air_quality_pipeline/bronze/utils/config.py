
URL = "https://eeadmz1-downloads-api-appservice.azurewebsites.net/"
ENDPOINT = "ParquetFile"

BUCKET = "aws-s3-air-quality-bucket-309159505215-eu-west-3-an"
ARCHIVES_PREFIX = "raw/eea/archives"
PARQUET_PREFIX = "raw/eea/parquet"

METADATA_URL = "https://discomap.eea.europa.eu/App/AQViewer/download?fqn=Airquality_Dissem.b2g.Measurements&f=csv"
METADATA_PREFIX = "raw/eea/metadata"

START_YEAR = 2020
START_MONTH = 1

END_YEAR = 2025
END_MONTH = 12

POLLUTANTS = ["PM2.5", "PM10", "NO2", "O3", "SO2"] # 6001, 5, 8, 7, 1

COUNTRIES = ["FR"]