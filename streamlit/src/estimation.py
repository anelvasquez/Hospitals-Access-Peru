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
    """
    # Detectar separador
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        first = f.readline()
    sep = ";" if first.count(";") > first.count(",") else ","

    # Leer de forma robusta (saltando filas dañadas)
    df = pd.read_csv(
        filepath,
        sep=sep,
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip"
        # ⚠️ Removido 'low_memory' que no es compatible con engine='python'
    )

    # Columnas claves (resueltas contra el CSV real)
    col_estado = _col(df, "Estado")
    col_norte  = _col(df, "NORTE")
    col_este   = _col(df, "ESTE")

    # Filtrar ACTIVO (robusto a espacios/minúsculas)
    df = df[df[col_estado].astype(str).str.strip().str.upper() == "ACTIVO"]

    # Asegurar que NORTE/ESTE sean numéricos
    df[col_norte] = pd.to_numeric(df[col_norte], errors="coerce")
    df[col_este]  = pd.to_numeric(df[col_este],  errors="coerce")

    # Coordenadas válidas
    df = df.dropna(subset=[col_norte, col_este])
    df = df[(df[col_norte] != 0) & (df[col_este] != 0)]

    # GeoDataFrame en UTM 18S -> WGS84
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[col_este], df[col_norte]),
        crs="EPSG:32718",  # UTM 18S
    ).to_crs("EPSG:4326")

    return gdf

def get_data_summary(gdf):
    """Resumen para métricas."""
    def safe_nunique(colname):
        # Busca la columna sin depender de mayúsculas
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