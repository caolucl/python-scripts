def monitorDockerStatsOnce() {
    def proc = "docker stats --no-stream --format '{{.Name}} CPU={{.CPUPerc}} MEM={{.MemUsage}}'".execute()
    proc.waitFor()

    def output = proc.in.text.trim()
    println "Docker Container Stats:"
    output.eachLine { line ->
        println line
    }
}

// Run only once
monitorDockerStatsOnce()
