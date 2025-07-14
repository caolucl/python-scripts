import pyodbc
import pandas as pd

# Connection config
server = 'your_server_hostname_or_ip'
database = 'master'
username = 'your_user'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'  # Or 18 if installed

# Establish connection
conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={database};
UID={username};
PWD={password};
Encrypt=yes;
TrustServerCertificate=no;
"""
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Monitor: Get database size info
db_size_query = """
SELECT
    DB_NAME(database_id) AS [Database],
    CAST(SUM(size) * 8 / 1024 AS FLOAT) AS SizeMB
FROM sys.master_files
GROUP BY database_id
"""
print("🔍 Database Sizes (MB):")
df = pd.read_sql(db_size_query, conn)
print(df)

# Monitor: Active connections
active_conn_query = """
SELECT 
    DB_NAME(dbid) AS [Database],
    COUNT(dbid) AS [Connections]
FROM sys.sysprocesses
WHERE dbid > 0
GROUP BY dbid
"""
print("\n🔌 Active Connections:")
df = pd.read_sql(active_conn_query, conn)
print(df)

# Monitor: CPU intensive queries
cpu_query = """
SELECT TOP 5 
    total_worker_time/1000 AS CPU_MS,
    execution_count,
    total_elapsed_time/1000 AS Duration_MS,
    (SELECT TEXT FROM sys.dm_exec_sql_text(sql_handle)) AS query_text
FROM sys.dm_exec_query_stats
ORDER BY total_worker_time DESC
"""
print("\n🔥 Top 5 CPU-Heavy Queries:")
df = pd.read_sql(cpu_query, conn)
print(df)

cursor.close()
conn.close()
