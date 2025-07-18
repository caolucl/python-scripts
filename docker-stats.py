import docker
import time

client = docker.from_env()

def monitor_containers():
    containers = client.containers.list()
    for container in containers:
        stats = container.stats(stream=False)

        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        cpu_percent = 0.0
        if system_delta > 0.0:
            cpu_percent = (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0

        mem_usage = stats["memory_stats"]["usage"]
        mem_limit = stats["memory_stats"]["limit"]
        mem_percent = (mem_usage / mem_limit) * 100.0

        print(f"\nContainer: {container.name}")
        print(f"  CPU Usage: {cpu_percent:.2f}%")
        print(f"  Memory Usage: {mem_usage / 1024 / 1024:.2f} MB / {mem_limit / 1024 / 1024:.2f} MB ({mem_percent:.2f}%)")

while True:
    monitor_containers()
    time.sleep(5)
