import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import numpy as np

#create API client
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

#perform query
#st.cache data only reruns when query changes or after 10 mins
@st.cache_data(ttl=660)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    #convert to list of dicts
    rows = [dict(row) for row in rows_raw]
    return rows


#query for pedidos & unidades by year
rows = run_query("SELECT EXTRACT(YEAR from data_venda) as Year, sum(quantidade_vendadetalhe) as amount_sold, sum(preco_unidade) as total_value, COUNT(*) as number_of_orders FROM dbt-certification-402119.dbt_amonteiro.fct_final GROUP BY EXTRACT(YEAR from data_venda)")

# Function to plot either amount_sold, total_value or number_of_orders by year on a line graph
def yearData(x):
    #choose specific value based on radio button text
    value = ""
    match x:
        case 'Amount Sold':
            value = "amount_sold"
        case 'Total Value':
            value = "total_value"
        case 'Number Of Orders':
            value = 'number_of_orders'

    #create dictionary with Year and selected column
    rows_dict = {}
    for row in rows:
        rows_dict[row["Year"]] = float(row[value])

    #plot values
    fig, ax = plt.subplots()
    ax.plot(rows_dict.keys(), rows_dict.values())
    #turn off scientific notation
    ax.yaxis.get_major_formatter().set_scientific(False)
    #set tickrate to 1 and only show 4 possible years
    plt.xticks(np.arange(min(rows_dict.keys()), max(rows_dict.keys())+1))
    #change labels based on value
    ax.set_xlabel("Years")
    match value:
        case 'amount_sold':
            ax.set_title("Amount Sold Per Year")
            ax.set_ylabel("Total Amount")
        case 'total_value':
            ax.set_title("Total Value Sold Per Year")
            ax.set_ylabel("Total Value in Dollars")
        case 'number_of_orders':
            ax.set_title("Number of Orders Per Year")
            ax.set_ylabel("Number of Orders")
    
    #show graph
    st.pyplot(fig)

#radio button to swap between different x values on line chart
yearRadio = st.radio(
    "Choose an x value",
    ["Amount Sold", "Total Value", "Number Of Orders"]
)
#call function based on selected radio button
yearData(yearRadio)