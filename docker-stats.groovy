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


def parseSize(String value) {
    if (!value) return 0
    def multiplier = [
        'kB': 1,
        'KB': 1,
        'MB': 1024,
        'MiB': 1024,
        'GB': 1024 * 1024,
        'GiB': 1024 * 1024
    ]
    def matcher = value.trim() =~ /([\d\.]+)([A-Za-z]+)/
    if (matcher.matches()) {
        def num = matcher[0][1] as BigDecimal
        def unit = matcher[0][2]
        return (num * (multiplier[unit] ?: 1)).toInteger()
    }
    return 0
}

def monitorDockerStatsOnce() {
    def format = "{{.Name}} {{.CPUPerc}} {{.MemUsage}} {{.BlockIO}}"
    def proc = ["docker", "stats", "--no-stream", "--format", format].execute()
    proc.waitFor()

    def output = proc.in.text.trim()

    output.eachLine { line ->
        def (name, cpuRaw, memRaw, ioRaw) = line.tokenize(' ')
        
        def cpu = cpuRaw.replace('%', '')
        def memParts = memRaw.tokenize('/')
        def memMB = parseSize(memParts[0]) / 1024.0  // back to MB
        def ioParts = ioRaw.tokenize('/')
        def ioTotal = parseSize(ioParts[0]) + parseSize(ioParts[1])

        println "${name}.cpu=${cpu}"
        println "${name}.mem=${String.format('%.2f', memMB)}"
        println "${name}.io=${ioTotal}"
    }
}

monitorDockerStatsOnce()
