# Infrastructre

What brave souls are wandering around in these parts? Infrastructure might be a bit big and scary, but don't worry, we'll get through this together. After reading this, you'll be able to:

- Understand the basic concepts of infrastructure as Code
- Understand basic terraform concepts
- Understand basic Azure concepts
- Be able to contribute to this infrastructure

## Overview
First of all, IaC (infrastructre as code) is a way of managing infrastructure in a declerative way. Imagine you are a customer at a resturant. You don't go into the kitchen and tell the chef how to cook your food, you just tell the waiter what you want and the chef will make it for you. This is the same way IaC works. You tell the cloud provider what you want, and they will make it for you. We use terraform to do this. Terraform is a tool that allows us to write code that will be translated into infrastructure. This is done by writing code using the hashicorp language HCL (Hashicorp Configuration Language). **The code should be written in a way that is easy to understand and easy to read.** This is because the code itelf is the documentation.

Now with that out of the way, let's get into the actual infrastructure. We use Azure as our cloud provider. This means that we use Azure to host our infrastructure. This documentation will not go into detail about how Azure works, but it will explain the basics of how we use it.

### Setup from scratch
If you are setting up the infrastructure from scratch, you will need to do a few things. First of all, you will need to setup a storage account to store the terraform state. This is done by running the following command ([source](https://learn.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage?tabs=azure-cli)):

```bash
#!/bin/bash
RESOURCE_GROUP_NAME=tfstate
STORAGE_ACCOUNT_NAME=tfstaterandomname # must be globaly unique
CONTAINER_NAME=tfstate

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location eastus

# Create storage account
az storage account create --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME --sku Standard_LRS --encryption-services blob

# Create blob container
az storage container create --name $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME
```

With that out of the way, you will need to create a service principal to use with terraform authentication to Azure. This is done by running the following commands ([source](https://learn.microsoft.com/en-us/azure/developer/terraform/get-started-cloud-shell-bash?tabs=bash)):

```bash
#!/bin/bash
export MSYS_NO_PATHCONV=1

SERVICE_PRINCIPAL_NAME=martin-terraform # Choose a name for the service principal, this is just an example
SUBSCRIPTION_ID=$(az account show --query id --output tsv) # if you have more subscriptions, do "az account list" to get the id of the subscription you want to use

az ad sp create-for-rbac --name $SERVICE_PRINCIPAL_NAME --role Contributor --scopes /subscriptions/$SUBSCRIPTION_ID
```

The command with output something similar to this:

```bash
{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "displayName": "martin-terraform",
  "name": "http://martin-terraform",
  "password": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

When working locally, the easiest way to add these values is to add them to the `~/.bashrc` file. This is done to simplify the terraform setup. Add the following lines to the `~/.bashrc` file:


```bash
export ARM_SUBSCRIPTION_ID="<azure_subscription_id>"
export ARM_TENANT_ID="<azure_subscription_tenant_id>"
export ARM_CLIENT_ID="<service_principal_appid>"
export ARM_CLIENT_SECRET="<service_principal_password>"
```

Remember to run `source ~/.bashrc` after you have added these values.😉


> Little recap on what we just did:
>
> - We created a storage account to store the terraform state
> - We created a service principal to authenticate against Azure
> - We added the values of the service principal to the `~/.bashrc` file


We are now ready to start working with terraform localy. We want to have a `dev`, `staging` and `prod` environment. This is done by creating terraform workspaces. You can create a workspace by running the following command:

```bash
terraform workspace new dev
terraform workspace new pre
terraform workspace new pro
```

Select the workspace you want to work in by running the following command:

```bash
terraform workspace select dev
```

Try changing the infrastructre a bit and run `terraform plan` to see what will be changed.




!!!!⚠️
Remember to delete your infra when you are done playing around with it. This is done by running the following command:

```bash
terraform destroy
```

