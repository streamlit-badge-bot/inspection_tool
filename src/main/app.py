import streamlit as st
import psycopg2
from sqlalchemy import create_engine
import pandas as pd
import requests
import matplotlib.pyplot as plt


config = {

    "DATABASE": {
        "NAME": "xdev",
        "HOST": "35.205.238.199",
        "USER": "edidev",
        "PASSWORD": "edidev",
        "METADATA_DB": "postgresql+psycopg2://edidev:edidev@35.205.238.199/xdev",
        "xdev": "postgresql+psycopg2://edidev:edidev@35.205.238.199:5432/xdev"
    }
}

st.title('EDI Satellite Measurement Inspection')


# def connect_to_db():
#     host = config["DATABASE"]["HOST"]
#     db_name = config["DATABASE"]["NAME"]
#     user = config["DATABASE"]["USER"]
#     password = config["DATABASE"]["PASSWORD"]
#     engine = create_engine(
#         "postgresql://{}:{}@{}/{}".format(user, password, host, db_name)
#     )
#     conn = engine.connect()
#     return conn


# conn = connect_to_db()


# def get_all_reservoirs(conn):
#     sql_all_reservoirs_in_db = "select distinct magnr from water.classifiedsatellitepoints"
#     df = pd.read_sql(sql_all_reservoirs_in_db, conn)
#     return list(df['magnr'].values)


# def magnr_to_magname(magnr):
#     sql_magnr_to_magname = "select magnavn from metadata.nve_maginfo nm where magnr={}".format(
#         magnr)
#     df = pd.read_sql(sql_magnr_to_magname, conn)
#     magname = df['magnavn'].values[0]
#     return magname

# list_of_magnrs = get_all_reservoirs(conn)
# list_of_reservoirs_with_number_and_name = ['{}  ({})'.format(
#     magnr_to_magname(magnr), magnr) for magnr in list_of_magnrs]


# reservoir_selection = st.selectbox(
#     'Select Reservoir',
#     list_of_reservoirs_with_number_and_name,
# )

# for reservoir in list_of_reservoirs_with_number_and_name:
#     st.button(reservoir)