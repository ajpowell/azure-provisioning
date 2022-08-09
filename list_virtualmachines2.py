# From https://github.com/Azure-Samples/virtual-machines-python-manage/blob/master/example.py


# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
# from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

# Retrieve the resource group to use, defaulting to "myResourceGroup".
resource_group = os.getenv("RESOURCE_GROUP_NAME", "test-cluster-rg")

compute_client = ComputeManagementClient(credential, subscription_id)

# List VMs in subscription
print('\nList VMs in subscription')
for vm in compute_client.virtual_machines.list_all():
    print("\tVM: {}".format(vm.name))

# List VM in resource group
print('\nList VMs in resource group')
for vm in compute_client.virtual_machines.list(resource_group):
    print("\tVM: {}".format(vm.name))
    print(vm)