import pyodbc

server='tcp:sql-3dchatbot-server.database.windows.net,1433'
database='3D-ChatbotDB'
username='SKT1'
password='asdf1234!'

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password+';Encrypt=yes;TrustServerCertificate=no;')

cursor = conn.cursor()

cursor.execute("""

""")
conn.commit()

conn.close()