# Infrastructre

What brave souls are wandering around in these parts? Infrastructure might be a bit big and scary, but don't worry, we'll get through this together. There are some comments in cuppled in the `/infrastructure` folder that might help you with questions about infra choices that was done when this was created.

## Overview
First of all, IaC (infrastructre as code) is a way of managing infrastructure in a declerative way. Imagine you are a customer at a resturant. You don't go into the kitchen and tell the chef how to cook your food, you just tell the waiter what you want and the chef will make it for you. This is the same way IaC works. You tell the cloud provider what you want, and they will make it for you. We use terraform to do this. Terraform is a tool that allows us to write code that will be translated into infrastructure. This is done by writing code using the hashicorp language HCL (Hashicorp Configuration Language). **The code should be written in a way that is easy to understand and easy to read.** This is because the code itelf is the documentation.

We use Azure as our cloud provider. This means that we use Azure to host our infrastructure. This documentation will not go into detail about how Azure works, but it will explain the basics of how we use it.

### You need
- Terraform cli
- Azure cli

### Contributing to the infrastructure
You need access to TIHLDE's Azure subscription to be able to contribute to the infrastructure. See Azure auth section from [Setup from scratch](#setup-from-scratch) for info about how to authenticate to Azure.

We have multiple enviroments for our infra, `dev` and `pro`. Dev is used for development and correspond to api-dev.tihlde.org and pro is used for production and correspond to api.tihlde.org. When you are working on the infrastructure, you should always work in the `dev` environment when playing. This is done by running the following command:

```bash
terraform init
terraform workspace select dev
```

After selecting the correct enviroment, you must have the correct `terraform.tfvars` file in the root of the project. This file contains the variables that are used to configure the infrastructure. Ask some of the other developers for the correct values. When you have the correct values, you can run `terraform plan -vars-file dev.tfvars` to see what will be changed. 

> ⚠️ Don't run "terraform apply -vars-file <<file.tfvars>>" if you don't know what you are doing. You need to be sure that this is correct and don't nuke our infra before applying any changes. Allways run the `plan` command first.

When you are done making changes, you can commit and push your changes to Github. DO NOT push your `*.tfvars` file to Github. These file contain sensitive information and should not be shared with randos.

### How to do common changes

#### Changing existing environment variables to new values

Switch to the terraform workspace where you want to make the change. 

```bash
terraform wokspace select dev
```

Make changes to the `dev.tfvars` file and run terraform plan to see what will be changed.

```bash
terraform plan -vars-file dev.tfvars
```

If everything looks good, you can apply the changes.

```bash
terraform apply -vars-file dev.tfvars
```

#### Adding new environment variables from tfvars file

Go to the file that manages containers and add a new `env` block on both lepton rest api and lepton celery. 

```hcl
env {
  name  = "MY_NEW_ENV_VAR"
  value = var.my_new_env_var
}
```

You allso need to pass this variable down into the terraform module `infrastucture` in the `inputs.tf` file.

```hcl
variable "my_new_env_var" {
  type = string
  sensitive = true # Add this if it is sensitive
}
```

Now add the variable to the `dev.tfvars` file and pass it down to the module.


After you are done, run terraform plan to see what will be changed. Then apply the changes.

### We are fucked! Something is absolutely broken

If you don't know how to do it, you should not do it.

* You can roll back the database max 7 days.
* You can go into the Azure portal and look at logs
* See if the container app revision is failing. 
* You can fix the fault, push new changes to github, restart the revision after new image is uploaded.
* You can access the running containers directly from browsers with portal to find issues. (I would rather recommend az cli for this)
* You can send a message to Azure support. (they can't access our infra so they only answer questions)
* You can do dirty migration hot-fixes directly from the containers. (celery container is best for this)

### Setup from scratch
If you are setting up the infrastructure from scratch, you will need to do a few things. First of all, you will need to setup a storage account to store the terraform state. This is done by running the following command ([source](https://learn.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage?tabs=azure-cli)):

```bash
#!/bin/bash
RESOURCE_GROUP_NAME=devops
STORAGE_ACCOUNT_NAME=tfstatetihlde # must be globaly unique
CONTAINER_NAME=tfstate

# Create resource group
az group create --name $RESOURCE_GROUP_NAME --location norwayeast

# Create storage account
az storage account create --resource-group $RESOURCE_GROUP_NAME --name $STORAGE_ACCOUNT_NAME --sku Standard_LRS --encryption-services blob

# Wait for a while... Azure is hella slow

# Create blob container
az storage container create --name $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME
```

With that out of the way, you will need to authenticate to Azure so that terraform can make talk to Azure. There are two easy options, first is to az login and select the correct subscription. The second option is to use a service principal account.

#### Auth option 1
```bash
az account set --subscription "<subscription_id>"
az login 
```

#### Auth option 2
You are now creating private credentials. Do not share this with anyone. Create seperate creds for each person.

[source](https://learn.microsoft.com/en-us/azure/developer/terraform/get-started-cloud-shell-bash?tabs=bash)
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
  "password": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

Then fill this in with the correct values and run it.
```bash
export ARM_SUBSCRIPTION_ID="<azure_subscription_id>"
export ARM_TENANT_ID="<azure_subscription_tenant_id>"
export ARM_CLIENT_ID="<service_principal_appid>"
export ARM_CLIENT_SECRET="<service_principal_password>"
```

### Running terraform

We are now ready to start working with terraform localy. We want to have a `dev` and `prod` environment. This is done by creating terraform workspaces. You can create a workspace by running the following command:

```bash
terraform workspace new dev
terraform workspace new pro
```

Select the workspace you want to work in by running the following command:

```bash
terraform workspace select dev
```

Create a `terraform.tfvars` file in the root of the project with ok values.

Try changing the infrastructre a bit and run `terraform plan -vars-file terraform.tfvars` to see what will be changed.


> ⚠️
Remember to delete your infra when you are done playing around with it. This is done by running the following command:

```bash
terraform destroy -vars-file terraform.tfvars
```