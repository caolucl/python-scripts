import pyodbc
import pandas as pd

# --- SQL Server connection config ---
server = 'your_server_hostname_or_ip'
database = 'master'
username = 'your_user'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'  # Ensure driver is installed

# --- Enable encrypted connection (SSL/TLS) ---
conn_str = f"""
DRIVER={driver};
SERVER={server};
DATABASE={database};
UID={username};
PWD={password};
Encrypt=yes;
TrustServerCertificate=yes;  -- Use 'no' in production with a trusted cert
"""

# Connect
conn = pyodbc.connect(conn_str)
print("✅ Connected to SQL Server.\n")

# --- 1. Database Size ---
print("📦 Database Sizes (MB):")
db_size_query = """
SELECT
    DB_NAME(database_id) AS [Database],
    CAST(SUM(size) * 8.0 / 1024 AS FLOAT) AS [Size_MB]
FROM sys.master_files
GROUP BY database_id
"""
print(pd.read_sql(db_size_query, conn))


# --- 2. Active Connections ---
print("\n🔌 Active Connections:")
active_conn_query = """
SELECT 
    DB_NAME(database_id) AS [Database],
    COUNT(session_id) AS [Active_Sessions]
FROM sys.dm_exec_sessions
WHERE database_id IS NOT NULL
GROUP BY database_id
"""
print(pd.read_sql(active_conn_query, conn))


# --- 3. Top CPU Queries ---
print("\n🔥 Top 5 CPU-Consuming Queries:")
cpu_query = """
SELECT TOP 5 
    total_worker_time / 1000 AS CPU_ms,
    execution_count,
    total_elapsed_time / 1000 AS Duration_ms,
    SUBSTRING(qt.text, (qs.statement_start_offset / 2) + 1,
        ((CASE qs.statement_end_offset
            WHEN -1 THEN DATALENGTH(qt.text)
            ELSE qs.statement_end_offset
          END - qs.statement_start_offset) / 2) + 1) AS query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS qt
ORDER BY total_worker_time DESC
"""
print(pd.read_sql(cpu_query, conn))


# --- 4. Disk I/O per DB/File ---
print("\n💾 Disk I/O per File:")
disk_io_query = """
SELECT 
    DB_NAME(database_id) AS [Database],
    file_id,
    num_of_reads,
    num_of_writes,
    (io_stall_read_ms / NULLIF(num_of_reads,0)) AS avg_read_ms,
    (io_stall_write_ms / NULLIF(num_of_writes,0)) AS avg_write_ms
FROM sys.dm_io_virtual_file_stats(NULL, NULL)
"""
print(pd.read_sql(disk_io_query, conn))


# --- 5. Memory Usage ---
print("\n🧠 Memory Usage Summary:")
memory_query = """
SELECT
    type,
    SUM(pages_kb)/1024.0 AS memory_MB
FROM sys.dm_os_memory_clerks
GROUP BY type
ORDER BY memory_MB DESC
"""
print(pd.read_sql(memory_query, conn))


# --- 6. CPU Usage (Session-Level) ---
print("\n⚙️ CPU Usage per Request:")
cpu_request_query = """
SELECT 
    session_id,
    status,
    command,
    total_elapsed_time / 1000.0 AS elapsed_sec,
    cpu_time / 1000.0 AS cpu_sec,
    DB_NAME(database_id) AS database_name
FROM sys.dm_exec_requests
WHERE session_id > 50
ORDER BY cpu_time DESC
"""
print(pd.read_sql(cpu_request_query, conn))

# Cleanup
conn.close()
