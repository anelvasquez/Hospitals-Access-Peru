import streamlit as st
import os
from estimation import load_and_filter_ipress, get_data_summary
from plots import create_hospital_map, create_department_bar

# Configuración de página
st.set_page_config(
    page_title="Hospitales en Perú",
    page_icon="🏥",
    layout="wide"
)

# Título principal
st.title("🏥 Análisis de Hospitales Operativos en Perú")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["📂 Descripción de Datos, "📊 Análisis Estático", "🌐 Mapas Dinámicos"])

# TAB 1: Data Description
with tab1:
    st.header("📋 Descripción de Datosxxxx")
    
    # Unidad de Análisis
    st.subheader("Unidad de Análisis")
    st.markdown("**Hospitales públicos operatssssivos** en el Perú")
    
    st.divider()
    
    # Fuentes de Datos
    st.subheader("Fuentes de Datos")
    
    st.markdown("""
    - **MINSA – IPRESS** (operational subset): Registro Nacional de Instituciones Prestadoras de Servicios de Salud
      - 🔗 URL: [Datos Abiertos Perú - MINSA IPRESS](https://datosabiertos.gob.pe/dataset/minsa-ipress)
    
    - **INEI**: Centros Poblados del Perú (Population Centers)
      - 🔗 URL: [Datos Abiertos Perú - Centros Poblados](https://datosabiertos.gob.pe/dataset/dataset-centros-poblados)
    
    - **Distritos del Perú**: Shapefile de límites administrativos (EPSG:4326)
    """)
    
    st.divider()
    
    # Reglas de Filtrado
    st.subheader("Reglas de Filtrado")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("✅ **Estado**")
        st.markdown("✅ **Coordenadas válidas**")
        st.markdown("✅ **Exclusión de nulos**")
    
    with col2:
        st.info("Solo hospitales con estado **'ACTIVO'**")
        st.info("Solo registros con coordenadas válidas (NORTE y ESTE)")
        st.info("Exclusión de coordenadas (0, 0) o valores nulos")
    
    st.divider()
    
    # Cargar datos
    @st.cache_data
    def load_data():
        # Ruta relativa desde src/ hacia data/
        csv_path = '../data/IPRESS.csv'
        if not os.path.exists(csv_path):
            # Intentar ruta alternativa
            csv_path = 'data/IPRESS.csv'
        return load_and_filter_ipress(csv_path)
    
    try:
        with st.spinner('⏳ Cargando y procesando datos...'):
            gdf_hospitals = load_data()
            summary = get_data_summary(gdf_hospitals)
        
        st.success('✅ Datos cargados y filtrados exitosamente')
        
        # Métricas principales
        st.subheader("📊 Resumen de Datos")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🏥 Total Hospitales",
                value=f"{summary['total_hospitals']:,}",
                help="Hospitales operativos filtrados"
            )
        
        with col2:
            st.metric(
                label="📍 Departamentos",
                value=summary['departments'],
                help="Número de departamentos con hospitales"
            )
        
        with col3:
            st.metric(
                label="🗺️ Provincias",
                value=summary['provinces'],
                help="Número de provincias cubiertas"
            )
        
        with col4:
            st.metric(
                label="🏘️ Distritos",
                value=summary['districts'],
                help="Número de distritos con servicios"
            )
        
        st.divider()
        
        # Vista previa de datos
        st.subheader("🔍 Vista Previa de Datos")
        
        # Columnas clave para mostrar
        display_columns = [
            'Nombre del establecimiento',
            'Departamento',
            'Provincia',
            'Distrito',
            'Categoria',
            'Estado',
            'Clasificación'
        ]
        
        # Filtrar solo las columnas que existen
        available_columns = [col for col in display_columns if col in gdf_hospitals.columns]
        
        st.dataframe(
            gdf_hospitals[available_columns].head(15),
            use_container_width=True,
            height=400
        )
        
        # Información adicional
        with st.expander("ℹ️ Información del Dataset"):
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown("**Dimensiones del dataset:**")
                st.write(f"- Filas: {len(gdf_hospitals):,}")
                st.write(f"- Columnas: {len(gdf_hospitals.columns)}")
            
            with col_info2:
                st.markdown("**Sistema de coordenadas:**")
                st.write(f"- Original: UTM 18S (EPSG:32718)")
                st.write(f"- Convertido a: WGS84 (EPSG:4326)")
        
        # Guardar en session_state para otros tabs
        st.session_state['gdf_hospitals'] = gdf_hospitals
        
    except FileNotFoundError as e:
        st.error("❌ No se encontró el archivo IPRESS.csv")
        st.info("💡 Asegúrate de que el archivo esté en la carpeta **data/**")
        
        with st.expander("🔍 Debug: Rutas verificadas"):
            st.write("Directorio actual:", os.getcwd())
            st.write("Buscando en:")
            st.code("../data/IPRESS.csv\ndata/IPRESS.csv")
        
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        
        with st.expander("Ver error completo"):
            import traceback
            st.code(traceback.format_exc())

# TAB 2: Análisis Estático
with tab2:
    st.header("📊 Análisis Estático de Mapas y Departamentos")
    
    if 'gdf_hospitals' in st.session_state:
        try:
            # Aquí irá el contenido del Tab 2
            st.info("🚧 Mapas estáticos con GeoPandas (próximamente)")
            
            # Gráfico de barras por departamento
            bar_chart = create_department_bar(st.session_state['gdf_hospitals'])
            st.plotly_chart(bar_chart, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción de Datos'**")

# TAB 3: Mapas Dinámicos
with tab3:
    st.header("🌐 Mapas Dinámicos")
    
    st.markdown("""
    - **National Folium choropleth + markers**: Mapa nacional con coropletas y marcadores
    - **Folium proximity maps for Lima & Loreto**: Mapas de proximidad para Lima y Loreto
    """)
    
    if 'gdf_hospitals' in st.session_state:
        try:
            st.info("🚧 Mapas interactivos con Folium (próximamente)")
            
            # Mapa básico (placeholder)
            map_fig = create_hospital_map(st.session_state['gdf_hospitals'])
            st.plotly_chart(map_fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción 