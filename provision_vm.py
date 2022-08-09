#
# From https://docs.microsoft.com/en-us/azure/developer/python/sdk/examples/azure-sdk-example-virtual-machines?tabs=cmd
#

# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
# from azure.mgmt.network.v2020_06_01.models import SecurityRule
import os
# import sys

# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
PREFIX = 'test-cluster'

RESOURCE_GROUP_NAME = PREFIX + "-rg"
LOCATION = "uksouth"

# VM ID
ID = '02'

# public_ip = True
public_ip = False



# Network and IP address names
VNET_NAME = PREFIX + "-vnet"
SUBNET_NAME = PREFIX + "-subnet"
IP_NAME = PREFIX + "-ip-" + ID
IP_CONFIG_NAME = PREFIX + "-ip-config-" + ID
NIC_NAME = PREFIX + "-nic-" + ID
NSG_NAME = PREFIX + "-nsg-" + ID

VM_NAME = "node" + ID
USERNAME = "azureuser"
# PASSWORD = "ChangePa$$w0rd24"  # Using privatekey

print('')
print(f"Provisioning a virtual machine...some operations might take a minute or two.")
print('')

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]


# Step 1: Provision a resource group

# Obtain the management object for resources, using the credentials from the CLI login.
resource_client = ResourceManagementClient(credential, subscription_id)

try:
    rg_result = resource_client.resource_groups.get(RESOURCE_GROUP_NAME)
    print(f" 1. Existing resource group {rg_result.name} found in the {rg_result.location} region")

except:
    # Provision the resource group.
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
        {
            "location": LOCATION
        }
    )
    print(f" 1. Provisioned resource group {rg_result.name} in the {rg_result.location} region")

# For details on the previous code, see Example: Provision a resource group
# at https://docs.microsoft.com/azure/developer/python/azure-sdk-example-resource-group


# Step 2: provision a virtual network

# A virtual machine requires a network interface client (NIC). A NIC requires
# a virtual network and subnet along with an IP address. Therefore we must provision
# these downstream components first, then provision the NIC, after which we
# can provision the VM.

# Obtain the management object for networks
network_client = NetworkManagementClient(credential, subscription_id)

try:
    vnet_result = network_client.virtual_networks.get(RESOURCE_GROUP_NAME, VNET_NAME)
    print(f" 2. Existing virtual network {vnet_result.name} found with address prefixes {vnet_result.address_space.address_prefixes}")

except:
    # Provision the virtual network and wait for completion
    poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
        VNET_NAME,
        {
            "location": LOCATION,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            }
        }
    )
    vnet_result = poller.result()
    print(f" 2. Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")


# Step 3: Provision the subnet and wait for completion
try:
    subnet_result = network_client.subnets.get(RESOURCE_GROUP_NAME, VNET_NAME, SUBNET_NAME)
    print(f" 3. Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

except:
    poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
        VNET_NAME, SUBNET_NAME,
        { "address_prefix": "10.0.0.0/24" }
    )
    subnet_result = poller.result()
    print(f" 3. Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")


# Step 4: Provision an IP address and wait for completion
try:
    ip_address_result = network_client.public_ip_addresses.get(RESOURCE_GROUP_NAME, IP_NAME)
    print(f" 4. Existing public IP address {ip_address_result.name} found with address {ip_address_result.ip_address}")

except:
    poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
        IP_NAME,
        {
            "location": LOCATION,
            "sku": {"name": "Standard"},
            "public_ip_allocation_method": "Static",
            "public_ip_address_version": "IPV4"
        }
    )
    ip_address_result = poller.result()
    print(f" 4. Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

if public_ip:
    # Step 5: Provision the network security group
    PORT_RULE_NAME = 'Allow port 22'

    try:
        nsg_result = network_client.network_security_groups.get(RESOURCE_GROUP_NAME, NSG_NAME)
        print(f" 5. Existing network security group {nsg_result.name} found.")

    except:
        nsg_params = NetworkSecurityGroup(
            id= NSG_NAME, 
            location=LOCATION, 
            tags={ "name" : NSG_NAME },
            security_rules=[{
                "protocol": 'Tcp', 
                "source_address_prefix": '*', 
                "destination_address_prefix": '*', 
                "access": 'Allow', 
                "direction": 'Inbound', 
                "description": PORT_RULE_NAME,
                "source_port_range": '*', 
                "destination_port_range": '22', 
                "priority": 100, 
                "name": PORT_RULE_NAME
                }]
            )
        poller = network_client.network_security_groups.begin_create_or_update(RESOURCE_GROUP_NAME, NSG_NAME, parameters=nsg_params)
        nsg_result = poller.result()
        print(f" 5. Provisioned network security group {nsg_result.name}")

    # Step 6: Provision the network interface client
    try:
        nic_result = network_client.network_interfaces.get(RESOURCE_GROUP_NAME, NIC_NAME)
        print(f" 6. Existing network interface client {nic_result.name} found")

    except:
        poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
            NIC_NAME, 
            {
                "location": LOCATION,
                "ip_configurations": [ {
                    "name": IP_CONFIG_NAME,
                    "subnet": { "id": subnet_result.id },
                    "public_ip_address": {"id": ip_address_result.id }
                }],
            'network_security_group': {
                'id': nsg_result.id
            }
            }
        )
        nic_result = poller.result()
        print(f" 6. Provisioned network interface client {nic_result.name} (Internet accessible)")

else:
    # Step 6: Provision the network interface client
    try:
        nic_result = network_client.network_interfaces.get(RESOURCE_GROUP_NAME, NIC_NAME)
        print(f" 6. Existing network interface client {nic_result.name} found")

    except:
        poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
            NIC_NAME, 
            {
                "location": LOCATION,
                "ip_configurations": [ {
                    "name": IP_CONFIG_NAME,
                    "subnet": { "id": subnet_result.id },
                    "public_ip_address": {"id": ip_address_result.id }
                }]
            }
        )
        nic_result = poller.result()
        print(f" 6. Provisioned network interface client {nic_result.name} (private)")



# Step 7: Provision the virtual machine

# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)

try:
    vm_result = compute_client.virtual_machines.get(RESOURCE_GROUP_NAME, VM_NAME)
    print(f"Existing virtual machine {vm_result.name} found")

except:
    print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

    # Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
    # on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

    poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
        {
            "location": LOCATION,
            "storage_profile": {
                "image_reference": {
                    "publisher": 'Canonical',
                    "offer": "0001-com-ubuntu-server-focal",
                    "sku": "20_04-lts-gen2",
                    "version": "latest"
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_B1s"
            },
            "os_profile": {
                "computer_name": VM_NAME,
                "admin_username": USERNAME,
                "linuxConfiguration": {
                    "disablePasswordAuthentication": True,
                    "ssh": {
                        "publicKeys": [
                            {
                                "path": "/home/azureuser/.ssh/authorized_keys",
                                "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC4b+tG9m4xR6z7KtSWs4ddbM0eAJAVEMPcNlbZfgyai7jSI5G48a6G+lry3xUQg/CV/nXdI8hCMZOfFyzxR2ix9hdZIKrRT9KaXL1Bfn7Oe/oLOvx6Dyb45VZ3hxeiMkAo2WHNHGHYmv4sYM8k0zzl4ykk70bd8UM4GWaHSkf3Z4VHgTN6B3K+QieZVmqpBiUD6N+b8fxRYBTj5EYc8HxipVHm/EXHQOwjZRbjFVYUNo78px36HCEU8KesxkdzWUqKnwXkl+I/yiV2t8c/F+REEyyHdmUykmmhlX//uzhiqFSBcXMwUQRUxHC9e9MqAgksntmsjPPYHTd7MuNSO6nYyq9OdUpVQvaoZufy2ZJLI2joM7n31ngAdRgw8m5hx5erMVBfnGtixcd8NWoJFmHB2tajajm2iubw40T0NZeRPAoPh3WcofmJorOVFr3DsjH8T9/55to0n6Wp0VJjdFUFaHcVZuH1sNcchdWJRpg+YzXLQHCBKZaEQOCWA4XATkU= generated-by-azure"
                            }
                        ]
                    }
                },
                "secrets": []
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": nic_result.id,
                }]
            }        
        }
    )
    vm_result = poller.result()
    print(f"Provisioned virtual machine {vm_result.name}")

print('')
print('Done.')
print('')
