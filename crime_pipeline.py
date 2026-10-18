import pandas as pd

df = pd.read_csv(
    "data/donnee-data.gouv-2025-geographie2026-produit-le2026-06-25.csv",
    sep=";",
    low_memory=False
)

print("Dimensions :", df.shape)

print("\nColonnes :")
print(df.columns.tolist())

print("\nAnnées disponibles :")
print(sorted(df["annee"].unique()))

print("\nNombre d'indicateurs :")
print(df["indicateur"].nunique())

print("\nExemple d'indicateurs :")
print(df["indicateur"].unique()[:20])