import pandas as pd
import geopandas as gpd

def _col(df, name):
    """Devuelve el nombre real de una columna (case-insensible y con espacios)."""
    key = name.strip().lower()
    for c in df.columns:
        if c.strip().lower() == key:
            return c
    raise KeyError(f"No se encontró la columna '{name}' en el CSV. Columnas: {list(df.columns)}")

def load_and_filter_ipress(filepath):
    """
    Carga IPRESS y filtra:
    - Estado == ACTIVO
    - NORTE/ESTE no nulos ni 0
    Convierte UTM 18S -> WGS84.
    Incluye diagnósticos para depuración.
    """
    # Detectar separador (coma o punto y coma)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        first = f.readline()
    sep = ";" if first.count(";") > first.count(",") else ","

    # Leer CSV robusto
    df = pd.read_csv(
        filepath,
        sep=sep,
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip",
        low_memory=False,
    )

    # ---------------------------
    # Diagnósticos iniciales
    # ---------------------------
    print("✅ Columnas detectadas:", df.columns.tolist())

    try:
        col_estado = _col(df, "Estado")
        print(f"📌 Columna 'Estado' encontrada como: {col_estado}")
        print("Valores únicos en Estado (primeros 20):", df[col_estado].unique()[:20])
    except Exception as e:
        print("❌ No se encontró columna Estado:", e)
        return pd.DataFrame()

    try:
        col_norte = _col(df, "NORTE")
        col_este  = _col(df, "ESTE")
        print(f"📌 Columnas coordenadas: {col_norte}, {col_este}")
        print("Ejemplo de coordenadas:\n", df[[col_norte, col_este]].head())
    except Exception as e:
        print("❌ No se encontraron columnas NORTE/ESTE:", e)
        return pd.DataFrame()

    # ---------------------------
    # Filtros
    # ---------------------------

    # Normalizar Estado
    df[col_estado] = df[col_estado].astype(str).str.strip().str.upper()

    # Filtrar por ACTIVO (contenga ACTIVO en cualquier variante)
    df = df[df[col_estado].str.contains("ACTIVO", na=False)]

    # Asegurar que NORTE/ESTE sean numéricos
    df[col_norte] = pd.to_numeric(df[col_norte], errors="coerce")
    df[col_este]  = pd.to_numeric(df[col_este],  errors="coerce")

    # Filtrar coordenadas válidas
    df = df.dropna(subset=[col_norte, col_este])
    df = df[(df[col_norte] != 0) & (df[col_este] != 0)]

    print("✅ Registros después de filtros:", len(df))

    # ---------------------------
    # Convertir a GeoDataFrame
    # ---------------------------
    if len(df) > 0:
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df[col_este], df[col_norte]),
            crs="EPSG:32718",  # UTM 18S
        ).to_crs("EPSG:4326")
        return gdf
    else:
        return df  # vacío

def get_data_summary(gdf):
    """Resumen simple de métricas."""
    if gdf is None or len(gdf) == 0:
        return {
            "total_hospitals": 0,
            "departments": 0,
            "provinces": 0,
            "districts": 0,
        }

    def safe_nunique(colname):
        for c in gdf.columns:
            if c.strip().lower() == colname.strip().lower():
                return gdf[c].nunique()
        return 0

    return {
        "total_hospitals": len(gdf),
        "departments": safe_nunique("Departamento"),
        "provinces":   safe_nunique("Provincia"),
        "districts":   safe_nunique("Distrito"),
    }

# ---------------------------
# Uso
# ---------------------------
if __name__ == "__main__":
    file_path = "IPRESS.csv"  # cambia a la ruta real si hace falta
    gdf = load_and_filter_ipress(file_path)
    summary = get_data_summary(gdf)
    print("📊 Resumen:", summary)