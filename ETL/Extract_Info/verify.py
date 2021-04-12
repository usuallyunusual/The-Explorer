import pandas as pd
import mysql
from mysql.connector import Error
try:
    conn = mysql.connector.connect(host='127.0.0.1',port = 3307,database='explorer_db',user='root',password = '')
    if conn.is_connected():
        print("Connection successful: ",conn.get_server_info())
    cur = conn.cursor()
    conn_2 = mysql.connector.connect(host='127.0.0.1',port = 3307,database='explorer_test',user='root',password = '')
    if conn_2.is_connected():
        print("Connection successful: ",conn.get_server_info())
    cur_2 = conn_2.cursor()
    cur.execute('''SELECT * FROM event''')
    data = pd.DataFrame(cur.fetchall())
    heads = list()
    for row in cur.description:
        heads.append(row[0])
    data.columns = heads
    data = data.sort_values(by = ["event_key"],ascending = True)
    #print(data.head())
    cur_2.execute('''SELECT * FROM event''')
    data_2 = pd.DataFrame(cur_2.fetchall())
    #print(data_2.head())
    heads = list()
    for row in cur_2.description:
        heads.append(row[0])
    data_2.columns = heads
    data_2 = data_2.sort_values(by = ["event_key"],ascending = True)
    print(len(data),len(data_2),len(data)==len(data_2))
    data.set_index("event_key")
    data_2.set_index("event_key")
    def get_different_rows(source_df, new_df):
        """Returns just the rows from the new dataframe that differ from the source dataframe"""
        merged_df = source_df.merge(new_df, indicator=True, how='outer')
        changed_rows_df = merged_df[merged_df['_merge'] == 'right_only']
        return changed_rows_df.drop('_merge', axis=1)
    net = get_different_rows(data,data_2)
    print(net)
    cur.close()
    cur_2.close()
    conn.close()
    conn_2.close()
except Error as e:
    print("Error while connecting to MySQL", e)