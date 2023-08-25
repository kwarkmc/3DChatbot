# DB 설정
import pyodbc
import datetime
import time

bvh_folder_path = "./BVH_files"

#Azure SQL DB Initialization 부분
server='tcp:sql-3dchatbot-server.database.windows.net,1433'
database='3D-ChatbotDB'
username='SKT1'
password=''

last_timestamp = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password+';Encrypt=yes;TrustServerCertificate=no;')

cursor = conn.cursor()

while True:
    insert_query = """
    SELECT TOP 1 * FROM BVHdb WHERE Timestamp > ? ORDER BY Timestamp DESC
    """

    cursor.execute(insert_query, last_timestamp)
    rows = cursor.fetchone()

    if rows:
        data_id = rows[0]
        timestamp = rows[1]
        motion_content = rows[2]
        label_name = rows[3]
        file_name = rows[4]
        file_data = rows[5]

        last_timestamp = timestamp

        bvh_file_path = f"{bvh_folder_path}/{file_name}.bvh"

        with open(bvh_file_path, 'wb') as file:
            file.write(file_data)

        print(f"""
                DATA DOWNLOADED!!
                DataID:          {data_id}
                Timestamp:       {timestamp}
                MotionContent:   {motion_content}
                LabelName:       {label_name}
                FileName:        {file_name}
                FileData (size): {len(file_data) if file_data else 0} bytes
                """)

    time.sleep(5) # 타이머 간격 (초)