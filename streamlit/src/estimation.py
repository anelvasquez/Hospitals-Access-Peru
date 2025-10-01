import pandas as pd
import geopandas as gpd

def _col(df, name):
    """Devuelve el nombre real de una columna (case-insensible y con espacios)."""
    key = name.strip().lower()
    for c in df.columns:
        if c.strip().lower() == key:
            return c
    raise KeyError(f"No se encontró la columna '{name}' en el CSV. Columnas disponibles: {list(df.columns)}")

def load_and_filter_ipress(filepath):
    """
    Carga IPRESS y filtra:
    - Estado == ACTIVO
    - NORTE/ESTE no nulos ni 0
    Convierte UTM 18S -> WGS84.
    """
    # Detectar separador automáticamente
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline()
    
    # Determinar separador (coma o punto y coma)
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    
    print(f"🔍 Detectado separador: '{sep}'")

    # Leer CSV con manejo robusto de errores
    df = pd.read_csv(
        filepath,
        sep=sep,
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip"
    )
    
    print(f"📊 Datos cargados: {len(df)} registros, {len(df.columns)} columnas")

    # Columnas según tu estructura real
    col_estado = _col(df, "Estado")
    col_norte  = _col(df, "NORTE")
    col_este   = _col(df, "ESTE")

    # Filtrar solo registros ACTIVOS
    df[col_estado] = df[col_estado].astype(str).str.strip().str.upper()
    df_active = df[df[col_estado] == "ACTIVO"].copy()
    
    print(f"✅ Filtrados con estado ACTIVO: {len(df_active)} registros")

    # Convertir coordenadas a numérico
    df_active[col_norte] = pd.to_numeric(df_active[col_norte], errors="coerce")
    df_active[col_este]  = pd.to_numeric(df_active[col_este],  errors="coerce")

    # Filtrar coordenadas válidas (no nulas y diferentes de 0)
    df_valid = df_active.dropna(subset=[col_norte, col_este])
    df_valid = df_valid[(df_valid[col_norte] != 0) & (df_valid[col_este] != 0)]
    
    print(f"✅ Con coordenadas válidas: {len(df_valid)} registros")

    # Crear GeoDataFrame en UTM 18S
    gdf = gpd.GeoDataFrame(
        df_valid,
        geometry=gpd.points_from_xy(df_valid[col_este], df_valid[col_norte]),
        crs="EPSG:32718"  # UTM Zone 18S (usado en Perú)
    )
    
    # Convertir a WGS84 (lat/lon estándar)
    gdf = gdf.to_crs("EPSG:4326")
    
    print(f"🌍 Convertido a WGS84 (EPSG:4326)")

    return gdf

def get_data_summary(gdf):
    """
    Genera resumen estadístico del GeoDataFrame.
    """
    def safe_nunique(colname):
        """Cuenta valores únicos de forma segura (case-insensitive)"""
        for c in gdf.columns:
            if c.strip().lower() == colname.strip().lower():
                return gdf[c].nunique()
        return 0

    summary = {
        "total_hospitals": len(gdf),
        "departments": safe_nunique("Departamento"),
        "provinces":   safe_nunique("Provincia"),
        "districts":   safe_nunique("Distrito"),
    }
    
    return summary