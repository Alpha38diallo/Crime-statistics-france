import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require"
)
csv_file = "data/donnee-data.gouv-2025-geographie2026-produit-le2026-06-25.csv"

print("Lecture du CSV...")

df = pd.read_csv(
    csv_file,
    sep=";",
    encoding="utf-8"
)

print(f"{len(df):,} lignes chargées")

print("Import dans PostgreSQL...")

df.to_sql(
    "crime_stats",
    engine,
    if_exists="replace",
    index=False,
    chunksize=10000,
    method="multi"
)

print("✅ Import terminé")