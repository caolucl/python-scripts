import pyodbc

# Connection parameters (LogicMonitor will replace ##HOSTNAME##)
server = "##HOSTNAME##"
username = "your_user"
password = "your_password"
driver = '{ODBC Driver 17 for SQL Server}'
default_db = 'master'

conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={default_db};
UID={username};
PWD={password};
Encrypt=yes;
TrustServerCertificate=yes;
"""

try:
    conn = pyodbc.connect(conn_str, timeout=5)
    cursor = conn.cursor()

    query = """
    SELECT name FROM sys.databases 
    WHERE state_desc = 'ONLINE' AND name NOT IN ('master', 'tempdb', 'model', 'msdb')
    """
    cursor.execute(query)
    for row in cursor.fetchall():
        print(row[0])  # This is the instance name LogicMonitor will track

    conn.close()

except Exception as e:
    print(f"error##exception##{str(e)}")
