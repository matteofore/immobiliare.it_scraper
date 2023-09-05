from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import re
from stqdm import stqdm

# function that modify the elements in the input_li that present space and "-" to allow the scraping link to be computed correctly
def formatting_input(input_li):
    for i, element in enumerate(input_li):
        for char in [" ", "'"]:
            element = element.replace(char, '-')
            input_li[i] = element
    return input_li

# function that from the input excel file create the list for the regions, provinces and municipalities
def input_li(input_file):
    data = pd.read_excel(input_file, header=None)
    region_li = data[0].dropna().unique().tolist()
    if 1 in data:
        province_li = data[1].dropna().unique().tolist()
    else:
        province_li = []
    if 2 in data:
        comune_li = data[2].dropna().unique().tolist()
    else:
        comune_li = []
    region_li = formatting_input(region_li)
    province_li = formatting_input(province_li)
    comune_li = formatting_input(comune_li)
    return region_li, province_li, comune_li

def format_number(number_str):
    return number_str.replace('.', '').replace(',', '.')

# function that given a link will enter and scrape the rows of the table of interest 
def table_rows(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'nd-table nd-table--borderBottom'})
    rows = table.find_all('tr')
    return rows



# function that performs the main scraping and output the dataframe containing the scraped data
def immobiliare_scraping(region_li, province_li, comune_li):

    url = "https://www.immobiliare.it/mercato-immobiliare/"
    data = []

    if len(region_li) == 0:
        region_rows = table_rows(url)

        for region_row in region_rows[1:]:
            region_columns = region_row.find_all('td')
            region_name = region_columns[0].text.strip()
            region_li.append(region_name)

    for region in stqdm(region_li, desc="Scraping of " + str(len(region_li)) + " regions"):
        region_link = url + str(region) + "/"

        if len(province_li) == 0:
            province_rows = table_rows(region_link)

            for province_row in province_rows[1:]:
                province_columns = province_row.find_all('td')
                province_name = province_columns[0].text.strip()
                province_li.append(province_name)

        for province in stqdm(province_li, desc="Scraping of " + str(len(province_li)) + " provinces"):
            province_link = region_link + str(province) + "-provincia/"
            comune_rows = table_rows(province_link)
            comune_info_li = []

            if len(comune_li) == 0:
                for comune_row in comune_rows[1:]:
                    comune_columns = comune_row.find_all('td')

                    vendita = format_number(comune_columns[1].text.strip())
                    affitto = format_number(comune_columns[2].text.strip())
                    comune_link = comune_columns[0].find('a')['href']
                    comune_name = comune_columns[0].text.strip()
                    comune_info_li.append([comune_name, vendita, affitto, comune_link])

            else:
                for comune_row in comune_rows[1:]:
                    comune_columns = comune_row.find_all('td')
                    comune_name = comune_columns[0].text.strip()

                    for comune in comune_li:
                        if comune_name == comune:
                            vendita = format_number(comune_columns[1].text.strip())
                            affitto = format_number(comune_columns[2].text.strip())
                            comune_link = comune_columns[0].find('a')['href']
                            comune_info_li.append([comune_name, vendita, affitto, comune_link])
                
            for comune_info in stqdm(comune_info_li, desc="Scraping of " + str(len(comune_info_li)) + " municipalities"):
                comune_name, comune_vendita, comune_affitto, comune_link = comune_info[0], comune_info[1], comune_info[2], comune_info[3]

                zona_rows = table_rows(comune_link) 
                zona_columns = zona_rows[1].find_all('td')
                zona_link = zona_columns[0].find('a')['href']

                if len(zona_link.split('/')) == 8:
                    for zona_row in stqdm(zona_rows[1:], desc="Scraping of " + str(len(zona_rows[1:]))+" neighborhoods of " + str(comune_name)):
                        zona_columns = zona_row.find_all('td')
                        zona_name = zona_columns[0].text.strip()
                        zona_link = zona_columns[0].find('a')['href']
                        zona_vendita = format_number(zona_columns[1].text.strip())
                        zona_affitto = format_number(zona_columns[2].text.strip())
                        indirizzo_response = requests.get(zona_link)
                        indirizzo_soup = BeautifulSoup(indirizzo_response.content, 'html.parser')
                        indirizzo_table = indirizzo_soup.find('table', {'class': 'nd-table nd-table--borderBottom'})

                        if indirizzo_table is None:
                            indirizzo_li = []
                        else:
                            indirizzo_rows = indirizzo_table.find_all('tr')
                            indirizzo_li = indirizzo_rows[1:]
                        data.append([region, province, comune_name, zona_name, indirizzo_li, zona_vendita, zona_affitto])
                else:
                    zona_name = '-'
                    indirizzo_li = []
                    zona_vendita = comune_vendita
                    zona_affitto = comune_affitto
                            
                    data.append([region, province, comune_name, zona_name, indirizzo_li, zona_vendita, zona_affitto])

    df = pd.DataFrame(data, columns=['Region', 'Province', 'Municipality', 'Neighborhood', 'List_of_addresses', 'Sale(€/m²)', 'Rent(€/m²)'])
    df.replace('-', np.nan, inplace=True)
    df['Sale(€/m²)'] = df['Sale(€/m²)'].astype(float)
    df['Rent(€/m²)'] = df['Rent(€/m²)'].astype(float)

    new_indirizzi = []
    for indirizzi in df['List_of_addresses']:
        new_indirizzo = []
        try:
            for indirizzo in indirizzi:
                indirizzo = str(indirizzo)
                regex = re.search(r'/">(.*?)<\/a>', indirizzo)
                new_indirizzo.append(regex.group(1))   
            new_indirizzi.append(new_indirizzo)
        except:
            new_indirizzi.append([])

    df['Addresses_in_neighborhood'] = new_indirizzi          
    df.drop(columns={"List_of_addresses"}, inplace=True)

    return df