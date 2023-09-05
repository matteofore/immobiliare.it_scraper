import streamlit as st
import plotly.figure_factory as ff
import plotly.express as px

st.markdown("# Analytics")

try:
    df = st.session_state.df

    st.write("This is the data upon which analytics are built.")

    st.dataframe(df)

    st.markdown("## Graphic Analytics")

    st.write("Graph describing the relationship between sale and rent of each municipality and/or area.")

    fig = px.scatter(
        df,
        x="Sale(€/m²)",
        y="Rent(€/m²)",
        color="Rent(€/m²)",
        color_continuous_scale="reds",
        hover_data=["Municipality", "Neighborhood"]
    )

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    st.write("Graph describing the distribution of the selling price and the rental price, both per square meter.")

    dist_type = st.radio(
        "Choose one of the two options to view its chart: ",
        ["Sale :house:", "Rent :money_with_wings:"])

    if dist_type == "Sale :house:":
        df['Municipality-Neighborhood'] = df['Municipality'] + '-' + df['Neighborhood'].astype(str)
        df.set_index('Municipality-Neighborhood', inplace=True)
        st.area_chart(df, y="Sale(€/m²)", color="#f5f5dc")

    if dist_type == "Rent :money_with_wings:":
        df['Municipality-Neighborhood'] = df['Municipality'] + '-' + df['Neighborhood'].astype(str)
        df.set_index('Municipality-Neighborhood', inplace=True)
        st.area_chart(df, y="Rent(€/m²)", color="#f5f5dc")
except:
    st.write("No data available, before scrape the desired information in the Home page.")


