import pandas as pd
import geopandas as gpd

def _col(df, name):
    """Devuelve el nombre real de una columna (case-insensible y con espacios)."""
    key = name.strip().lower()
    for c in df.columns:
        if c.strip().lower() == key:
            return c
    raise KeyError(f"No se encontró la columna '{name}' en el archivo. Columnas disponibles: {list(df.columns)}")

def load_and_filter_ipress(filepath):
    """
    Carga IPRESS desde Excel y filtra:
    - Solo registros con NORTE y ESTE válidos (no vacíos, no cero)
    - Estado == ACTIVO (opcional, comentado por ahora)
    Convierte UTM 18S -> WGS84.
    """
    # Leer archivo Excel (primer sheet por defecto)
    df = pd.read_excel(filepath, sheet_name=0)
    
    print(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
    print(f"Primeras columnas: {df.columns[:5].tolist()}")

    try:
        col_norte  = _col(df, "NORTE")
        col_este   = _col(df, "ESTE")
        col_dept   = _col(df, "Departamento")
        col_prov   = _col(df, "Provincia")
        col_dist   = _col(df, "Distrito")
    except KeyError as e:
        print(f"Error: {e}")
        raise

    # Convertir coordenadas a numérico
    df[col_norte] = pd.to_numeric(df[col_norte], errors="coerce")
    df[col_este]  = pd.to_numeric(df[col_este],  errors="coerce")

    # Contar registros con coordenadas antes del filtro
    total_con_coords = df[[col_norte, col_este]].notna().all(axis=1).sum()
    print(f"Registros con NORTE y ESTE no vacíos: {total_con_coords}")

    # Filtrar coordenadas válidas (no nulas y diferentes de 0)
    df_valid = df.dropna(subset=[col_norte, col_este])
    df_valid = df_valid[(df_valid[col_norte] != 0) & (df_valid[col_este] != 0)].copy()
    
    print(f"Registros con coordenadas válidas (no vacías y != 0): {len(df_valid)}")

    if len(df_valid) == 0:
        print("ADVERTENCIA: No se encontraron registros con coordenadas válidas")
        return gpd.GeoDataFrame()

    # Crear GeoDataFrame en UTM 18S
    gdf = gpd.GeoDataFrame(
        df_valid,
        geometry=gpd.points_from_xy(df_valid[col_este], df_valid[col_norte]),
        crs="EPSG:32718"
    )
    
    # Convertir a WGS84
    gdf = gdf.to_crs("EPSG:4326")
    
    print(f"Convertido a WGS84 (EPSG:4326)")
    print(f"Departamentos únicos: {gdf[col_dept].nunique()}")
    print(f"Provincias únicas: {gdf[col_prov].nunique()}")
    print(f"Distritos únicos: {gdf[col_dist].nunique()}")

    return gdf

def get_data_summary(gdf):
    """Genera resumen estadístico del GeoDataFrame."""
    if len(gdf) == 0:
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

    summary = {
        "total_hospitals": len(gdf),
        "departments": safe_nunique("Departamento"),
        "provinces":   safe_nunique("Provincia"),
        "districts":   safe_nunique("Distrito"),
    }
    
    return summary

def get_departments_list(gdf):
    """Obtiene lista ordenada de departamentos únicos."""
    for c in gdf.columns:
        if c.strip().lower() == "departamento":
            return sorted(gdf[c].dropna().unique().tolist())
    return []

def count_hospitals_by_district(gdf):
    """Cuenta hospitales por distrito y retorna un DataFrame."""
    # Buscar columnas de ubicación
    col_dept = None
    col_prov = None
    col_dist = None
    col_ubigeo = None
    
    for c in gdf.columns:
        c_lower = c.strip().lower()
        if c_lower == "departamento":
            col_dept = c
        elif c_lower == "provincia":
            col_prov = c
        elif c_lower == "distrito":
            col_dist = c
        elif c_lower == "ubigeo":
            col_ubigeo = c
    
    if not col_dist:
        return pd.DataFrame()
    
    # Contar por distrito
    counts = gdf.groupby([col_dept, col_prov, col_dist]).size().reset_index(name='n_hospitales')
    
    # Agregar UBIGEO si existe
    if col_ubigeo:
        ubigeo_map = gdf.groupby(col_dist)[col_ubigeo].first().to_dict()
        counts['UBIGEO'] = counts[col_dist].map(ubigeo_map)
    
    return counts