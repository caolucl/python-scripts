import groovy.sql.Sql

def server   = hostProps.get("system.hostname")
def username = hostProps.get("sql.user")
def password = hostProps.get("sql.pass")
def driver   = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
def defaultDb = "master"

// JDBC connection string
def url = "jdbc:sqlserver://${server};databaseName=${defaultDb};encrypt=true;trustServerCertificate=true"

def props = new Properties()
props.setProperty("user", username)
props.setProperty("password", password)

def sql = null
try {
    sql = Sql.newInstance(url, props, driver)

    // Get list of user databases
    def dbs = []
    sql.eachRow("""
        SELECT name FROM sys.databases
        WHERE state_desc = 'ONLINE' AND name NOT IN ('master','tempdb','model','msdb')
    """) {
        dbs << it.name
    }

    dbs.each { db ->
        try {
            // CPU Time (ms)
            def cpuTime = 0
            sql.eachRow("USE [${db}]; SELECT SUM(cpu_time) as cpu FROM sys.dm_exec_requests WHERE database_id = DB_ID()") {
                cpuTime = it.cpu ?: 0
            }

            // RAM Usage (MB)
            def ramMb = 0
            sql.eachRow("USE [${db}]; SELECT SUM(virtual_memory_committed_kb)/1024.0 as ram FROM sys.dm_os_memory_clerks") {
                ramMb = it.ram ?: 0
            }

            // Log File Size (GB)
            def logGb = 0
            sql.eachRow("""
                USE [${db}];
                SELECT SUM(size) * 8.0 / 1024 / 1024 as logSize
                FROM sys.master_files
                WHERE type_desc = 'LOG' AND database_id = DB_ID()
            """) {
                logGb = it.logSize ?: 0
            }

            println "${db}##cpu_ms##${String.format('%.2f', cpuTime)}"
            println "${db}##ram_mb##${String.format('%.2f', ramMb)}"
            println "${db}##log_file_gb##${String.format('%.2f', logGb)}"

        } catch (Exception innerEx) {
            println "${db}##error##${innerEx.message}"
        }
    }

} catch (Exception ex) {
    println "error##connection##${ex.message}"
} finally {
    if (sql) {
        sql.close()
    }
}
