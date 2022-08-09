# From: https://docs.microsoft.com/en-us/azure/developer/python/sdk/examples/azure-sdk-example-list-resource-groups

# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

# Retrieve the resource group to use, defaulting to "myResourceGroup".
resource_group = os.getenv("RESOURCE_GROUP_NAME", "test-cluster-rg")

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

# Initialize the compute management client with the RunAs credential and specify the subscription to work against.
compute_client = ComputeManagementClient(credential, subscription_id)

# Retrieve the list of resources in "myResourceGroup" (change to any name desired).
# The expand argument includes additional properties in the output.
resource_list = resource_client.resources.list_by_resource_group(
    resource_group, expand="createdTime,changedTime")

# Show the groups in formatted output
column_width = 36

print('')
print("Resource".ljust(column_width) + "Type".ljust(column_width)
      + "Create date".ljust(column_width)  + "VM Status".ljust(column_width)
      )
print("-" * (column_width * 4))

for resource in list(resource_list):
    if resource.type == 'Microsoft.Compute/virtualMachines':
        # Get vm status
        vm = compute_client.virtual_machines.get(resource_group, resource.name, expand='instanceView')

        # These are the statuses of the VM about the event execution status and the vm state, the vm state is the second one.
        vm_statuses = vm.instance_view.statuses
        # print(vm_statuses[1].display_status)

        print(f"{resource.name:<{column_width}}{resource.type:<{column_width}}"
          f"{str(resource.created_time):<{column_width}}{str(vm_statuses[1].display_status):<{column_width}}")
#  f"{str(resource.created_time):<{column_width}}{str(vm_statuses[1].display_status):<{column_width}}")

print("=" * (column_width * 4))
print('')
