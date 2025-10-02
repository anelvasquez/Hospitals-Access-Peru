import streamlit as st
import os
from estimation import load_and_filter_ipress, get_data_summary, get_departments_list
from plots import create_hospital_map, create_department_bar
import matplotlib
matplotlib.use('Agg')  # Backend para Streamlit

# Configuración de página
st.set_page_config(
    page_title="Hospitales en Perús",
    page_icon="🏥",
    layout="wide"
)

# Título principal
st.title("🏥 Análisis de Hospitales Operativos en Perú")

# Crear tabs
tab1, tab2, tab3 = st.tabs(["📂 Descripción de Datos", "📊 Análisis Estático", "🌍 Mapas Dinámicos"])

# TAB 1: Data Description (SIN CAMBIOS)
with tab1:
    st.header("📋 Descripción de Datos")
    
    # Unidad de Análisis
    st.subheader("Unidad de Análisis")
    st.markdown("**Hospitales públicos operativos** en el Perú")
    
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
        # Buscar archivo Excel en data/
        excel_path = '../data/IPRESS.xlsx'
        if not os.path.exists(excel_path):
            excel_path = 'data/IPRESS.xlsx'
        if not os.path.exists(excel_path):
            raise FileNotFoundError("No se encontró IPRESS.xlsx en la carpeta data/")
        return load_and_filter_ipress(excel_path)
    
    try:
        with st.spinner('⏳ Cargando y procesando datos desde Excel...'):
            gdf_hospitals = load_data()
            
            # Verificar si hay datos
            if len(gdf_hospitals) == 0:
                st.error("❌ No se encontraron datos después del filtrado")
                st.info("🔍 Revisa la terminal/consola para ver los mensajes de debug")
                st.stop()
            
            summary = get_data_summary(gdf_hospitals)
        
        st.success(f'✅ Datos cargados: {len(gdf_hospitals)} hospitales con coordenadas válidas')
        
        # Métricas principales en 3 columnas
        st.subheader("📊 Resumen de Datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🏥 Total de Hospitales",
                value=f"{summary['total_hospitals']:,}",
                help="Total de hospitales con coordenadas válidas"
            )
        
        with col2:
            st.metric(
                label="📍 Departamentos",
                value=summary['departments'],
                help="Número de departamentos cubiertos"
            )
        
        with col3:
            st.metric(
                label="🏘️ Distritos",
                value=summary['districts'],
                help="Número de distritos con hospitales"
            )
        
        st.divider()
        
        # Gráfico de distribución por departamento
        st.subheader("📊 Distribución por Distrito")
        
        # Obtener conteo por departamento
        col_dept = None
        for c in gdf_hospitals.columns:
            if c.strip().lower() == "departamento":
                col_dept = c
                break
        
        if col_dept:
            dept_counts = gdf_hospitals[col_dept].value_counts().sort_values(ascending=False)
            
            import plotly.graph_objects as go
            
            fig = go.Figure(data=[
                go.Bar(
                    x=dept_counts.index,
                    y=dept_counts.values,
                    marker=dict(
                        color='#60a5fa',
                        line=dict(color='#2563eb', width=1)
                    ),
                    text=dept_counts.values,
                    textposition='outside',
                    textfont=dict(size=12, color='white')
                )
            ])
            
            fig.update_layout(
                height=500,
                margin=dict(l=40, r=40, t=40, b=120),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title="",
                    showgrid=False,
                    showline=False,
                    tickfont=dict(color='white', size=11),
                    tickangle=-45
                ),
                yaxis=dict(
                    title="",
                    showgrid=True,
                    gridcolor='rgba(128,128,128,0.2)',
                    showline=False,
                    tickfont=dict(color='white', size=11)
                ),
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Filtro por Departamento
        st.subheader("🔎 Filtrar por Departamento")
        
        departments = get_departments_list(gdf_hospitals)
        selected_dept = st.selectbox(
            "Selecciona un departamento:",
            options=["Todos"] + departments,
            index=0
        )
        
        # Aplicar filtro
        if selected_dept != "Todos":
            # Buscar columna Departamento
            col_dept = None
            for c in gdf_hospitals.columns:
                if c.strip().lower() == "departamento":
                    col_dept = c
                    break
            
            if col_dept:
                gdf_filtered = gdf_hospitals[gdf_hospitals[col_dept] == selected_dept]
                st.info(f"Mostrando {len(gdf_filtered)} hospitales en **{selected_dept}**")
            else:
                gdf_filtered = gdf_hospitals
        else:
            gdf_filtered = gdf_hospitals
        
        st.divider()
        
        # Vista previa de datos
        st.subheader("🔍 Vista Previa de Datos")
        
        # Columnas clave para mostrar
        display_columns = [
            'Institución',
            'Nombre del establecimiento',
            'Departamento',
            'Provincia',
            'Distrito',
            'Categoria',
            'Estado',
            'NORTE',
            'ESTE'
        ]
        
        # Filtrar solo las columnas que existen
        available_columns = [col for col in display_columns if col in gdf_filtered.columns]
        
        if len(available_columns) > 0:
            st.dataframe(
                gdf_filtered[available_columns].head(20),
                use_container_width=True,
                height=400
            )
        else:
            st.warning("⚠️ No se encontraron las columnas esperadas")
            st.write("Columnas disponibles:", gdf_filtered.columns.tolist())
        
        # Información adicional
        with st.expander("ℹ️ Información del Dataset"):
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.markdown("**Dimensiones del dataset:**")
                st.write(f"- Filas totales: {len(gdf_hospitals):,}")
                st.write(f"- Filas mostradas: {len(gdf_filtered):,}")
                st.write(f"- Columnas: {len(gdf_hospitals.columns)}")
            
            with col_info2:
                st.markdown("**Sistema de coordenadas:**")
                st.write(f"- Original: UTM 18S (EPSG:32718)")
                st.write(f"- Convertido a: WGS84 (EPSG:4326)")
        
        # Guardar en session_state para otros tabs
        st.session_state['gdf_hospitals'] = gdf_hospitals
        st.session_state['gdf_filtered'] = gdf_filtered
        
    except FileNotFoundError as e:
        st.error("❌ No se encontró el archivo IPRESS.xlsx")
        st.info("💡 Asegúrate de que el archivo esté en la carpeta **data/** y se llame **IPRESS.xlsx**")
        
        with st.expander("🔍 Debug: Rutas verificadas"):
            st.write("Directorio actual:", os.getcwd())
            st.write("Buscando en:")
            st.code("../data/IPRESS.xlsx\ndata/IPRESS.xlsx")
        
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        
        with st.expander("Ver error completo"):
            import traceback
            st.code(traceback.format_exc())

# TAB 2: Análisis Estático (NUEVOS MAPAS)
with tab2:
    st.header("🗺️ Mapas Estáticos y Análisis por Departamento")
    
    if 'gdf_hospitals' not in st.session_state:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción de Datos'**")
    else:
        try:
            # Cargar shapefile de distritos
            @st.cache_data
            def load_districts():
                # Buscar v_distritos_2023.shp
                shapefile_path = '../data/v_distritos_2023.shp'
                if not os.path.exists(shapefile_path):
                    shapefile_path = 'data/v_distritos_2023.shp'
                if not os.path.exists(shapefile_path):
                    raise FileNotFoundError("No se encontró v_distritos_2023.shp")
                
                from estimation import load_districts_shapefile, merge_hospitals_with_districts
                gdf_dist = load_districts_shapefile(shapefile_path)
                
                # Hacer merge con hospitales
                gdf_merged = merge_hospitals_with_districts(
                    st.session_state['gdf_hospitals'], 
                    gdf_dist
                )
                
                return gdf_dist, gdf_merged
            
            with st.spinner('📍 Cargando shapefile de distritos...'):
                gdf_districts, gdf_districts_merged = load_districts()
            
            st.success(f'✅ Shapefile cargado: {len(gdf_districts)} distritos')
            
            st.divider()
            
            # SECCIÓN 1: Mapa Nacional Coroplético
            st.subheader("🗺️ Mapa Nacional: Hospitales por Distrito")
            
            with st.spinner('Generando mapa coroplético...'):
                from plots import create_static_choropleth_map
                
                fig_choropleth = create_static_choropleth_map(
                    gdf_districts_merged,
                    title="Distribución de Hospitales por Distrito en Perú"
                )
                
                st.pyplot(fig_choropleth)
            
            # Estadísticas del mapa
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_hosp = gdf_districts_merged['n_hospitales'].sum()
                st.metric("🏥 Total Hospitales", f"{int(total_hosp):,}")
            
            with col2:
                distritos_con_hosp = (gdf_districts_merged['n_hospitales'] > 0).sum()
                st.metric("🏘️ Distritos con Hospitales", f"{distritos_con_hosp:,}")
            
            with col3:
                distritos_sin_hosp = (gdf_districts_merged['n_hospitales'] == 0).sum()
                st.metric("❌ Distritos sin Hospitales", f"{distritos_sin_hosp:,}")
            
            st.divider()
            
            # SECCIÓN 2: Gráfico de Barras por Departamento
            st.subheader("📊 Top 10 Departamentos")
            
            bar_chart = create_department_bar(st.session_state['gdf_hospitals'])
            st.plotly_chart(bar_chart, use_container_width=True)
            
            st.divider()
            
            # SECCIÓN 3: Mapa por Departamento
            st.subheader("🔍 Análisis por Departamento")
            
            departments = get_departments_list(st.session_state['gdf_hospitals'])
            selected_dept = st.selectbox(
                "Selecciona un departamento para ver su mapa:",
                options=departments,
                key='dept_selector_tab2'
            )
            
            if selected_dept:
                with st.spinner(f'Generando mapa de {selected_dept}...'):
                    from plots import create_department_static_map
                    
                    fig_dept = create_department_static_map(
                        gdf_districts,
                        st.session_state['gdf_hospitals'],
                        selected_dept
                    )
                    
                    st.pyplot(fig_dept)
                
                # Tabla de resumen del departamento
                col_dept = None
                for c in st.session_state['gdf_hospitals'].columns:
                    if c.strip().lower() == "departamento":
                        col_dept = c
                        break
                
                if col_dept:
                    gdf_dept = st.session_state['gdf_hospitals'][
                        st.session_state['gdf_hospitals'][col_dept] == selected_dept
                    ]
                    
                    # Contar por distrito
                    col_dist = None
                    for c in gdf_dept.columns:
                        if c.strip().lower() == "distrito":
                            col_dist = c
                            break
                    
                    if col_dist:
                        dist_counts = gdf_dept[col_dist].value_counts().reset_index()
                        dist_counts.columns = ['Distrito', 'Cantidad de Hospitales']
                        
                        st.markdown(f"**📋 Hospitales por Distrito en {selected_dept}**")
                        st.dataframe(
                            dist_counts,
                            use_container_width=True,
                            height=300
                        )
            
        except FileNotFoundError as e:
            st.error("❌ No se encontró el archivo v_distritos_2023.shp")
            st.info("💡 Asegúrate de que el shapefile esté en la carpeta **data/** con sus archivos asociados (.shp, .shx, .dbf, .prj)")
            
            with st.expander("🔍 Debug: Archivos buscados"):
                st.write("Buscando en:")
                st.code("../data/v_distritos_2023.shp\ndata/v_distritos_2023.shp")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
            with st.expander("Ver error completo"):
                import traceback
                st.code(traceback.format_exc())

# TAB 3: Mapas Dinámicos (SIN CAMBIOS)
with tab3:
    st.header("🌍 Mapas Dinámicos")
    
    st.markdown("""
    - **National Folium choropleth + markers**: Mapa nacional con coropletas y marcadores
    - **Folium proximity maps for Lima & Loreto**: Mapas de proximidad para Lima y Loreto
    """)
    
    if 'gdf_filtered' in st.session_state:
        try:
            st.info("🚧 Mapas interactivos con Folium (próximamente)")
            
            # Mapa básico
            map_fig = create_hospital_map(st.session_state['gdf_filtered'])
            st.plotly_chart(map_fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("⚠️ Primero carga los datos en la pestaña **'Descripción de Datos'**")