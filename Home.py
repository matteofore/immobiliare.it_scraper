import streamlit as st
import pandas as pd
from immobiliare_scraping import immobiliare_scraping, input_li, formatting_input
import io

def user_input(input_li, tipologia):
    input_str = st.text_input("(optional) Insert the " + str(tipologia))    
    if input_str:
        input_items = [item.capitalize() for item in input_str.split(', ')]
        input_li.extend(input_items)
    input_li = formatting_input(input_li)
    return input_li

# list that contains all the region in Italy 
REGIONS = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "friuli-venezia-giulia", "Lazio", "Liguria", 
           "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", "trentino-alto-adige", 
           "Umbria", "valle-d-aosta", "Veneto"]

# dictionaty that contains all the italian provinces associated to the respective region
PROVINCES = {
    "Abruzzo": ["Chieti", "L'Aquila", "Pescara", "Teramo"],
    "Basilicata": ["Potenza", "Matera"],
    "Calabria": ["Catanzaro", "Cosenza", "Crotone", "Reggio Calabria", "Vibo Valentia"],
    "Campania": ["Avellino", "Benevento", "Caserta", "Napoli", "Salerno"],
    "Emilia-Romagna": ["Bologna", "Ferrara", "Forlì-Cesena", "Modena", "Parma", "Piacenza", "Ravenna", "Reggio Emilia", "Rimini"],
    "friuli-venezia-giulia": ["Gorizia", "Pordenone", "Trieste", "Udine"],
    "Lazio": ["Frosinone", "Latina", "Rieti", "Roma", "Viterbo"],
    "Liguria": ["Genova", "Imperia", "La Spezia", "Savona"],
    "Lombardia": ["Bergamo", "Brescia", "Como", "Cremona", "Lecco", "Lodi", "Mantova", "Milano", "Monza e della Brianza", "Pavia", "Sondrio", "Varese"],
    "Marche": ["Ancona", "Ascoli Piceno", "Fermo", "Macerata", "Pesaro e Urbino"],
    "Molise": ["Campobasso", "Isernia"],
    "Piemonte": ["Alessandria", "Asti", "Biella", "Cuneo", "Novara", "Torino", "Verbania", "Vercelli"],
    "Puglia": ["Bari", "Barletta-Andria-Trani", "Brindisi", "Foggia", "Lecce", "Taranto"],
    "Sardegna": ["Cagliari", "Nuoro", "Oristano", "Sassari", "Sud Sardegna"],
    "Sicilia": ["Agrigento", "Caltanissetta", "Catania", "Enna", "Messina", "Palermo", "Ragusa", "Siracusa", "Trapani"],
    "Toscana": ["Arezzo", "Firenze", "Grosseto", "Livorno", "Lucca", "Massa e Carrara", "Pisa", "Pistoia", "Prato", "Siena"],
    "trentino-alto-adige": ["Bolzano", "Trento"],
    "Umbria": ["Perugia", "Terni"],
    "valle-d-aosta": ["Aosta"],
    "Veneto": ["Belluno", "Padova", "Rovigo", "Treviso", "Venezia", "Verona", "Vicenza"]
    }

st.write("""
# Immobiliare.it Scraper
Choose between the two input modes to use the scraper.\n
For both modes if no data is provided, the program will try to do the scraping of the entire Italian territory (it will take several hours). Otherwise, if
a region is provided, information from all the provinces in the region will be extracted. You can also select specific provinces within a 
region. Finally, it is possible to focus on the individual municipalities provided, but the region and province to which they belong should be previously indicated.
""")

region_li, province_li, comune_li = ([] for i in range(3))

example_df = pd.DataFrame([["Friuli venezia giulia", "Udine"], ["Valle d'aosta", ""]])

on = st.toggle('Change the input mode')

if on:
    uploaded_file = st.file_uploader("Load an excel file")
    st.write("""This an example of the dataframe to be uplaoded. In the first column you should put the region name, then in the second column a province name that is within the
             previously identified regions, but you can also leave it blank (if you want to scrape the entire region). In the end, it's also optional the municipalities that are
             within the provinces in the second column.""")
    st.dataframe(example_df)
    if uploaded_file:
        region_li, province_li, comune_li = input_li(uploaded_file)

else:
    st.write("Insert manually the region, province and municipality.")
    selected_regions = st.multiselect("Select the regions", REGIONS)
    available_provinces = [province for region in selected_regions for province in PROVINCES.get(region, [])]
    selected_provinces = st.multiselect("Select the provinces", available_provinces)
    region_li = selected_regions
    province_li = selected_provinces
    comune_li = user_input(comune_li, "municipality (in case you want to enter more than one, just separate them with a comma)")

if region_li == []:
    st.write("You are trying to do the scraping of the entire Italian territory, this will take several hours to complete.")

if province_li == [] and region_li != []:
    st.write("You are trying to scrap one or more regions, depending on the selected region and its connection, it may take several minutes.")

scrape = st.button("Scrape", type="primary", key="data")
if scrape:
    df = immobiliare_scraping(region_li, province_li, comune_li)

    if df not in st.session_state:
        st.session_state.df = df

    st.write("You can sort the results by clicking on the respective column.")
    st.dataframe(df)

    buffer = io.BytesIO()

    col1, buff, col2 = st.columns([2,1,2])

    with col1:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

            writer.close()

            st.download_button( 
                label='Download data as Excel',
                data=buffer,
                file_name='immobiliare_report.xlsx',
                mime='application/vnd.ms-excel'
            )

    with col2:
        @st.cache_data
        def convert_df_to_csv(data):
            return data.to_csv(index=False).encode('utf-8')


        st.download_button(
        label="Download data as CSV",
        data=convert_df_to_csv(df),
        file_name='immobiliare_report.csv',
        mime='text/csv',
        )
        
