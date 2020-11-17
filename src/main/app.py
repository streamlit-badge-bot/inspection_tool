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

def connect_to_db():
    host = config["DATABASE"]["HOST"]
    db_name = config["DATABASE"]["NAME"]
    user = config["DATABASE"]["USER"]
    password = config["DATABASE"]["PASSWORD"]
    engine = create_engine(
        "postgresql://{}:{}@{}/{}".format(user, password, host, db_name)
    )
    conn = engine.connect()
    return conn


conn = connect_to_db()