import SessionState
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import re

session_state = SessionState.get(checkboxed=False)

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


def get_measurements(conn):
    sql_new_measurements = "select id, magnr, acqdate, waterlevel, inspected, quality ->> 'score' as quality from water.classifiedsatellitepoints_ c"
    df = pd.read_sql(sql_new_measurements, conn)
    df['quality'] = pd.to_numeric(df['quality'])
    return df


def get_list_of_reservoirs(df):
    return list(df['magnr'][df['inspected'] == False].unique())


def get_historical_water_data(conn, magnr):
    sql_get_historical_filling_level = "\
        select \
            timestamp, waterlevel \
        from metadata.nve_ \
            where magnr={} \
            and waterlevel > 0 \
        order by \
            timestamp asc".format(
        magnr
    )
    df = pd.read_sql(sql_get_historical_filling_level, conn)
    df = df.set_index('timestamp', drop=True)
    return df


def get_historical_stats(conn, magnr):
    df = get_historical_water_data(conn, magnr)
    df = df.resample('W').mean()
    df['week'] = df.index.isocalendar().week
    ddf = df.groupby('week').mean()
    ddf['max'] = df.groupby('week').max()
    ddf['min'] = df.groupby('week').min()
    ddf = ddf.rename(columns={'waterlevel': 'median'})
    ddf = ddf.reset_index()
    return ddf


def magnr_to_magname(magnr):
    sql_magnr_to_magname = "select magnavn from metadata.nve_maginfo nm where magnr={}".format(
        magnr)
    df = pd.read_sql(sql_magnr_to_magname, conn)
    magname = df['magnavn'].values[0]
    return magname


conn = connect_to_db()

df = get_measurements(conn)

start_date = st.sidebar.date_input('start date', min_value=min(
    df['acqdate']), max_value=max(df['acqdate']), value=min(df['acqdate']))
end_date = st.sidebar.date_input('end date', min_value=min(
    df['acqdate']), max_value=max(df['acqdate']), value=max(df['acqdate']))

df = df[(df['acqdate'].dt.date > start_date)
        & (df['acqdate'].dt.date < end_date)]

satellite_score = st.sidebar.slider(
    'score', min_value=0.0, max_value=1.0, step=0.05, value=0.6)
df = df[df['quality'] >= satellite_score]
df = df.round(2)

reseroirs = get_list_of_reservoirs(df)

reservoirs_with_number_and_name = ['{}  ({})'.format(
    magnr_to_magname(magnr), magnr) for magnr in reseroirs]

reservoir_selection = st.sidebar.multiselect(
    'select reservoirs', reservoirs_with_number_and_name, default=reservoirs_with_number_and_name)


reservoir_selection_magnrs = (
    [re.findall('\((.*?)\)', i)[-1] for i in reservoir_selection])


for index, row in df[df['magnr'].isin(reservoir_selection_magnrs)].head(10).iterrows():
    button_label = 'magnr: {} id:{} date:{} score:{:.2f}'.format(row['magnr'],
                                                                 row['id'], row['acqdate'].date(), row['quality'])
    with st.beta_expander(button_label):
        df = df[df['magnr'] == row['magnr']]
        fig = px.scatter(df[df['inspected'] == False],
                         x='acqdate', y='waterlevel', hover_data=['acqdate', 'quality'])
        fig.add_trace(go.Scatter(
            x=df['acqdate'][df['inspected'] == True], y=df['waterlevel'][df['inspected'] == True], name='inspected', hovertext=df['quality']))
        fig.add_annotation(x=row['acqdate'], y=row['waterlevel'],
                           text='<b>score {:.2f}'.format(
                                row['quality']),
                           showarrow=True,
                           arrowhead=6,
                           arrowcolor='red',
                           arrowsize=2,
                           )
        fig.update_xaxes(rangeslider_visible=True)
        st.plotly_chart(fig, use_container_width=True)
        col1, col2 = st.beta_columns(2)

        if col1.button('Approve {}'.format(row['id'])):
            sql_approve = 'update water.classifiedsatellitepoints_ set inspected = true where id = {}'.format(
                row['id'])
            conn.execute(sql_approve)
            st.write('success')
            st.experimental_rerun()
        if col2.button('Reject {}'.format(row['id'])):
            sql_reject = 'update water.classifiedsatellitepoints_ set inspected = true, outlier = true where id = {}'.format(
                row['id'])
            conn.execute(sql_reject)
            st.write('success')
            st.experimental_rerun()


# for reservoir in reseroirs[:2]:
#     if st.button(str(reservoir)):
#         # hdf = get_historical_stats(conn, reservoir)
#         df = df[df['magnr'] == reservoir]
#         # df['week'] = df['acqdate'].dt.isocalendar().week
#         # df = pd.merge(hdf, df)
#         # st.dataframe(df.tail(20))
#         for index, row in df[:5].iterrows():
#             button_label = 'id:{} date:{} score:{:.2f}'.format(
#                 row['id'], row['acqdate'].date(), row['quality'])
#             with st.beta_expander(button_label):
#                 fig = px.scatter(df[df['inspected'] == False],
#                                  x='acqdate', y='waterlevel')
#                 fig.add_trace(go.Scatter(
#                     x=df['acqdate'][df['inspected'] == True], y=df['waterlevel'][df['inspected'] == True]))
#                 fig.add_annotation(x=row['acqdate'], y=row['waterlevel'],
#                                    text='score {:.2f}'.format(
#                                        row['quality']),
#                                    showarrow=True,
#                                    arrowhead=6,
#                                    arrowcolor='red',
#                                    arrowsize=2)
#                 fig.update_xaxes(rangeslider_visible=True)
#                 st.plotly_chart(fig, use_container_width=True)
#                 col1, col2 = st.beta_columns(2)
#                 st.write(session_state.checkboxed)

#                 if col1.button('Approve {}'.format(row['id'])):
#                     #sql_approve = 'update water.classifiedpoints_ c set c.inspected = true where c.id = {}'.format(row['id'])
#                     #conn.execute(sql_approve)
#                     st.write('qwe')
#                 if col2.button('Reject {}'.format(row['id'])) or session_state.checkboxed:
#                     st.write('asd')
#                 if st.button('Submit {}'.format(row['id'])):
#                     st.write('success')
