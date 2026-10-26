import os

size = 0

apath = "src/air_quality_pipeline/ingestion/data"

for path, dirs, files in os.walk(apath):
    for f in files:
        fp = os.path.join(path, f)
        size += os.path.getsize(fp)

print(f"Size: {size} bytes")