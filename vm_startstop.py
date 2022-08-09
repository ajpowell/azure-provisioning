
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


VM_NAME = 'node02'
GROUP_NAME = resource_group

"""
# Start the VM
print('\nStart VM')
async_vm_start = compute_client.virtual_machines.begin_start(GROUP_NAME, VM_NAME)
async_vm_start.wait()

# Restart the VM
print('\nRestart VM')
async_vm_restart = compute_client.virtual_machines.begin_restart(GROUP_NAME, VM_NAME)
async_vm_restart.wait()


# Stop the VM
print('\nStop VM')
async_vm_stop = compute_client.virtual_machines.begin_power_off(GROUP_NAME, VM_NAME)
async_vm_stop.wait()

# Deallocate VM
print('\nDeallocate VM')
async_vm_deallocate = compute_client.virtual_machines.begin_deallocate(GROUP_NAME, VM_NAME)
async_vm_deallocate.wait()


# Delete VM
print('\nDelete VM')
async_vm_delete = compute_client.virtual_machines.begin_delete(GROUP_NAME, VM_NAME)
async_vm_delete.wait()

"""

VM_NAME = 'node00'
# Run command on the VM
print('\nRun command on VM')
run_command_parameters = {
       'command_id': 'RunShellScript',  # For linux, don't change it
       'script': [
           'cat /proc/version'
       ]
   }
poller = compute_client.virtual_machines.begin_run_command(
         GROUP_NAME,
         VM_NAME,
         run_command_parameters
   )
result = poller.result()  # Blocking till executed
print(result.value[0].message)  # stdout/stderr


