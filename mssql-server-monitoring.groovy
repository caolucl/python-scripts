import groovy.sql.Sql

def server   = hostProps.get("system.hostname")
def username = hostProps.get("sql.user")
def password = hostProps.get("sql.pass")
def driver   = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
def defaultDb = "master"

def urlTemplate = { dbName ->
    return "jdbc:sqlserver://${server};databaseName=${dbName};encrypt=true;trustServerCertificate=true"
}

def props = new Properties()
props.setProperty("user", username)
props.setProperty("password", password)

def mainSql = null

try {
    mainSql = Sql.newInstance(urlTemplate(defaultDb), props, driver)

    // Get list of online user databases
    def dbs = []
    mainSql.eachRow("""
        SELECT name FROM sys.databases 
        WHERE state_desc = 'ONLINE' AND name NOT IN ('master', 'tempdb', 'model', 'msdb')
    """) {
        dbs << it.name
    }

    // Loop through each DB
    dbs.each { dbName ->
        def dbSql = null
        try {
            dbSql = Sql.newInstance(urlTemplate(dbName), props, driver)

            // --- 1. Active Connections ---
            def connCount = 0
            dbSql.eachRow("""
                SELECT COUNT(session_id) AS count
                FROM sys.dm_exec_sessions 
                WHERE database_id = DB_ID()
            """) {
                connCount = it.count ?: 0
            }
            println "${dbName}##active_connections##${connCount}"

            // --- 2. Database Size in GB ---
            def sizeGb = 0
            dbSql.eachRow("""
                SELECT SUM(size) * 8.0 / 1024 AS size_mb
                FROM sys.master_files
                WHERE database_id = DB_ID()
            """) {
                def sizeMb = it.size_mb ?: 0
                sizeGb = sizeMb / 1024.0
            }
            println "${dbName}##storage_gb##${String.format('%.2f', sizeGb)}"

            // --- 3. Log File Size in GB ---
            def logGb = 0
            dbSql.eachRow("""
                SELECT SUM(size) * 8.0 / 1024 / 1024 AS log_gb
                FROM sys.master_files
                WHERE type_desc = 'LOG' AND database_id = DB_ID()
            """) {
                logGb = it.log_gb ?: 0
            }
            println "${dbName}##log_file_gb##${String.format('%.2f', logGb)}"

            // --- 4. CPU Time (ms) ---
            def cpuTime = 0
            dbSql.eachRow("""
                SELECT SUM(cpu_time) AS cpu_ms
                FROM sys.dm_exec_requests
                WHERE database_id = DB_ID()
            """) {
                cpuTime = it.cpu_ms ?: 0
            }
            println "${dbName}##cpu_ms##${cpuTime}"

        } catch (Exception dbEx) {
            println "${dbName}##error##${dbEx.message}"
        } finally {
            if (dbSql != null) dbSql.close()
        }
    }

    // --- Global CPU (Top Query) ---
    def cpuMs = 0
    mainSql.eachRow("""
        SELECT TOP 1 total_worker_time / 1000.0 AS cpu_ms
        FROM sys.dm_exec_query_stats
        ORDER BY total_worker_time DESC
    """) {
        cpuMs = it.cpu_ms ?: 0
    }
    println "global##cpu_ms##${String.format('%.2f', cpuMs)}"

    // --- Global Memory ---
    def memoryMb = 0
    mainSql.eachRow("""
        SELECT SUM(pages_kb)/1024.0 AS memory_mb
        FROM sys.dm_os_memory_clerks
    """) {
        memoryMb = it.memory_mb ?: 0
    }
    println "global##memory_mb##${String.format('%.2f', memoryMb)}"

} catch (Exception ex) {
    println "error##exception##${ex.message}"
} finally {
    if (mainSql != null) mainSql.close()
}
