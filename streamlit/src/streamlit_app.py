import streamlit as st
from estimation import execute_regressions, generate_data
from plots import *

data = generate_data()
results, results_data = execute_regressions(data)

st.set_page_config(page_title="Geospatial Analysis of Hospitals in Peru", layout="wide")

tab1, tab2, tab3 = st.tabs(["Data Description", "Static Maps & Department Analysis", "Dynamic Maps"])

with tab1:

        st.markdown(
"""
# Data Description

Unit of analysis: operational public hospitals in Peru.
Data sources: MINSA - IPRESS (operational subset), Population Centers.
Filtering rules: only operational hospitals with valid lat/long.

"""
        )
        col1, col2 = st.columns([1, 2])
        st.write("---")

        with col1:
                st.markdown("### Options")
                segregated = st.checkbox(label="Segregate by age")
                fit_line = st.checkbox(label="Show regression line", value=True)
                st.write("---")
                

        fig = get_figure(results_data, segregated, fit_line, )
        table = get_table(results, segregated)

        with col1:
                st.markdown("### Regression Results")
                st.table(table)



        with col2:
                st.markdown("### Scatter Plot")
                st.plotly_chart(fig, use_container_width=True)
                st.write("---")
                st.markdown("### DAG")
                if segregated:
                        st.image("assets/segregated.png")
                else:
                        st.image("assets/aggregated.png")

with tab2:
        st.markdown("""

# Static Maps & Department Analysis

Embed static maps created with GeoPandas.
Include the department summary table and bar chart.                  

"""
)

with tab3:
        st.markdown("""
# Dynamic Maps:

National Folium choropleth + markers.
Folium proximity maps for Lima & Loreto.                    
"""
)



