🔧 Prerequisites
#Assign Reader role to your resource:
az role assignment create \
  --assignee <identity-object-id> \
  --role Reader \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Sql/servers/<sql-server>/databases/<db-name>
#Install Python packages:
pip install azure-identity azure-mgmt-monitor

#Ensure your script is running in an Azure environment with System Assigned Managed Identity enabled.

# how to call the script
python azure-sql-monitor-using-system-identity.py \
  --subscription-id "xxxx" \
  --resource-group "my-rg" \
  --sql-server "my-server" \
  --sql-db "mydb"

from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--subscription-id', required=True)
parser.add_argument('--resource-group', required=True)
parser.add_argument('--sql-server', required=True)
parser.add_argument('--sql-db', required=True)
args = parser.parse_args()

subscription_id = args.subscription_id
resource_group = args.resource_group
sql_server = args.sql_server
sql_db = args.sql_db

# Azure resource identifiers
#subscription_id = "<your-subscription-id>"
#resource_group = "<your-resource-group>"
#sql_server = "<your-sql-server-name>"
#sql_db = "<your-sql-database-name>"

# Azure SQL Database resource ID
resource_id = (
    f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
    f"providers/Microsoft.Sql/servers/{sql_server}/databases/{sql_db}"
)

# Authenticate using managed identity
credential = DefaultAzureCredential()

# Initialize Azure Monitor client
monitor_client = MonitorManagementClient(credential, subscription_id)

# Time range: last 30 minutes
end_time = datetime.datetime.utcnow()
start_time = end_time - datetime.timedelta(minutes=30)

# Metrics to collect
metric_names = [
    "cpu_percent",
    "dtu_consumption_percent",
    "connection_count",
    "storage_percent"
]

# Call Azure Monitor API
metrics = monitor_client.metrics.list(
    resource_uri=resource_id,
    timespan=f"{start_time}/{end_time}",
    interval="PT5M",
    metricnames=",".join(metric_names),
    aggregation="Average"
)

# Print results
for item in metrics.value:
    print(f"\nMetric: {item.name.localized_value}")
    for timeseries in item.timeseries:
        for data in timeseries.data:
            value = data.average
            if "storage" in item.name.value.lower() and value:
                # Convert bytes to TB if the value is in bytes
                tb_value = value / (1024 ** 4)
                print(f"  Time: {data.time_stamp} | Value: {value:.2f} bytes ({tb_value:.4f} TB)")
            else:
                print(f"  Time: {data.time_stamp} | Value: {value}")
