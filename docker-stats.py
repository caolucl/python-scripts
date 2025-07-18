import docker
import time

client = docker.from_env()

def monitor_containers():
    containers = client.containers.list()
    for container in containers:
        try:
            stats = container.stats(stream=False)

            # Get the number of CPUs
            percpu = stats["cpu_stats"]["cpu_usage"].get("percpu_usage")
            num_cpus = len(percpu) if percpu else 1

            # Calculate CPU usage
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]

            cpu_percent = 0.0
            if system_delta > 0.0 and cpu_delta > 0.0:
                cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0

            # Memory usage
            mem_usage = stats["memory_stats"].get("usage", 0)
            mem_limit = stats["memory_stats"].get("limit", 1)
            mem_percent = (mem_usage / mem_limit) * 100.0

            # CPU usage in seconds
            cpu_usage_in_seconds = cpu_delta / 1000000000  # from nanoseconds

            print(f"{container.name}.CPU_Used_Sec={cpu_usage_in_seconds:.6f}")
            print(f"{container.name}.CPU_Usage_Percent={cpu_percent:.2f}")
            print(f"{container.name}.Memory_Usage_MB={mem_usage / 1024 / 1024:.2f}")
        
        except Exception as e:
            print(f"Failed to fetch stats for {container.name}: {e}")

while True:
    monitor_containers()
    time.sleep(5)
