# Tested on Python 3.9

# import statement START
import time
from datetime import datetime
# from snowflake.snowpark.session import Session
import tzlocal
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import snowflake.connector
import streamlit as st
from plotly.subplots import make_subplots
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import os

# import statement END

# タイトル
st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center; color: #1489a6;'>❄❄ SN❄WFLAKE TABLE MANAGER ❄❄</h1>",
    unsafe_allow_html=True)

# 時間
from datetime import datetime
def current_dt():
    now = datetime.now()
    datetime_string = now.strftime("%d-%m-%Y %H:%M:%S")
    return datetime_string

# 接続
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        **st.secrets["snowflake"], client_session_keep_alive=True
    )

conn = init_connection()

@st.cache_data(ttl=600)
@st.cache_resource
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

query = "SELECT * FROM snowflake.account_usage.tables where table_type='BASE TABLE' order by last_altered desc limit 10"
# 結果をデータフレームに変換する
df = pd.read_sql_query(query, conn)
# データフレームを表示する
st.dataframe(df)

# テーブル数を出力する
total_table_count = "SELECT COUNT(table_id) FROM snowflake.account_usage.tables where deleted is null and table_type='BASE TABLE';"
total_table_count_inc_deleted = "SELECT COUNT(table_id) FROM snowflake.account_usage.tables where table_type='BASE TABLE';"
cursor = conn.cursor()
# total_table_count
cursor.execute(total_table_count)
# 結果を取得する
total_table_count = cursor.fetchone()[0]

# total_table_count_inc_deleted
cursor.execute(total_table_count_inc_deleted)
# 結果を取得する
total_table_count_inc_deleted = cursor.fetchone()[0]
# 結果を表示する
st.title("Overview of tables")

# 3つのメトリクスを2列で表示する
columns = st.columns(2)
columns[0].metric("Table Count", total_table_count)
columns[1].metric("Total Table Count Include Deleted", total_table_count_inc_deleted)

# クエリを実行し、結果をPandasのデータフレームに変換する
monthly_table = """
SELECT
    DATE_TRUNC('MONTH', created)::date AS date,
    COUNT(table_id) AS count
FROM
    snowflake.account_usage.tables
GROUP BY 1
ORDER BY 1
"""

monthly_table = pd.read_sql(monthly_table, conn)

st.write(monthly_table)

chart_data = pd.DataFrame(
    {'date': monthly_table.iloc[:,0],
    'table_count': monthly_table.iloc[:,0]}
)

data = {
        'date': monthly_table.iloc[:,0],
        'number_of_tables': monthly_table.iloc[:,1]
        }

daily_table_df = pd.DataFrame(data)
daily_table_df['date'] = pd.to_datetime(daily_table_df['date'])
st.line_chart(daily_table_df.set_index('date'))


# データのエクスポート
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

daily_table_df = convert_df(daily_table_df)
if st.button('Export テーブル数の推移'):
    label="Download data as CSV",
    data=daily_table_df,
    file_name='count_of_table.csv',
    mime='text/csv'