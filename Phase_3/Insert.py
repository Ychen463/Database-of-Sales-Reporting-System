# from flask import Flask, render_template, request, url_for
# from flask_mysqldb import MySQL
import pymysql
import pandas as pd
# import xlrd

db = pymysql.connect(host="localhost",
                     port = 3307,
                     user="root",
                     passwd="team030",
                     db="cs6401")


# insert_to_tmp_tbl_stmt = f"INSERT INTO {MY_TABLE} VALUES (?,?)"
#df['measurement'] = [format(i, '.3f') for i in df['measurement']]

df = pd.read_csv('/Users/reisturm/Desktop/sales.csv',low_memory=False)

print(df)

cur = db.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS Sales_5(
    quantity_sold varchar(50) NOT NULL,
    day varchar(50) NOT NULL,
    store_ID varchar(50) NOT NULL,
    PID varchar(50) NOT NULL,
    UNIQUE KEY(day, store_ID,PID)
        );
            """)
cnt = 0
for row in df.itertuples():
    print(row)
    data = (
        str(row[1]),
        str(row[2]),
        str(row[3]),
        str(row[4]),
    )
    query = f'''
                INSERT INTO Sales_5 (quantity_sold, day,store_id, PID)
                VALUES ('{str(row[1])}','{str(row[2])}','{str(row[3])}','{str(row[4])}');
                '''
    print(query)

    cur.execute(query)

    cnt = cnt + 1
    if cnt > 50:
        break
    print(data)

cur.commit()
cur.close()

# cursor = conn.cursor()
# cursor.fast_executemany = True
# cursor.executemany(insert_to_tmp_tbl_stmt, df.values.tolist())
# print(f'{len(df)} rows inserted to the {MY_TABLE} table')
# cursor.commit()
# cursor.close()
# conn.close()
