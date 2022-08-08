# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
# from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2020_06_01.models import SecurityRule
import os

print(f"Provisioning a virtual machine...some operations might take a minute or two.")

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]


# Step 1: Provision a resource group

# Obtain the management object for resources, using the credentials from
# the CLI login.
resource_client = ResourceManagementClient(credential, subscription_id)

# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you
# want.
RESOURCE_GROUP_NAME = "PythonAzureExample-VM-rg"
LOCATION = "uksouth"

# Network and IP address names
VNET_NAME = "python-example-vnet"
SUBNET_NAME = "python-example-subnet"
IP_NAME = "python-example-ip"
IP_CONFIG_NAME = "python-example-ip-config"
NIC_NAME = "python-example-nic"
NSG_NAME = "python-example-nsg3"

# Obtain the management object for networks
network_client = NetworkManagementClient(credential, subscription_id)

# Step 5a: Provision the network security group
PORT_RULE_NAME='Allow port 22'

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

print(f"Provisioned network security group {nsg_result.name}")
