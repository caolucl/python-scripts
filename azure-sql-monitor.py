from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
import datetime

# Credentials
TENANT_ID = "<your-tenant-id>"
CLIENT_ID = "<your-client-id>"
CLIENT_SECRET = "<your-client-secret>"
SUBSCRIPTION_ID = "<your-subscription-id>"

# Target resource
RESOURCE_GROUP = "<your-resource-group-name>"
SQL_SERVER = "<your-sql-server-name>"
SQL_DB = "<your-sql-database-name>"

# Resource ID for Azure SQL Database
resource_id = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/"
    f"providers/Microsoft.Sql/servers/{SQL_SERVER}/databases/{SQL_DB}"
)

# Authenticate
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# Initialize clients
monitor_client = MonitorManagementClient(credential, SUBSCRIPTION_ID)

# Time range: last 30 minutes
end_time = datetime.datetime.utcnow()
start_time = end_time - datetime.timedelta(minutes=30)

# Metrics to fetch
metrics_list = [
    "cpu_percent",
    "dtu_consumption_percent",
    "connection_count",
    "storage_percent"
]

# Get metrics
metrics_data = monitor_client.metrics.list(
    resource_id,
    timespan=f"{start_time}/{end_time}",
    interval="PT5M",
    metricnames=",".join(metrics_list),
    aggregation="Average"
)

# Display results
for item in metrics_data.value:
    print(f"\nMetric: {item.name.localized_value}")
    for timeseries in item.timeseries:
        for data in timeseries.data:
            print(f"  Time: {data.time_stamp} | Value: {data.average}")
