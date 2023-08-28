terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.68.0"
    }
  }
  #   # Update this block with the location of your terraform state file
  #   backend "azurerm" {
  #     resource_group_name  = "rg-terraform-github-actions-state"
  #     storage_account_name = "terraformgithubactions"
  #     container_name       = "tfstate"
  #     key                  = "lepton.tfstate"
  #     use_oidc             = true
  #   }
}

provider "azurerm" {
  features {}
}

module "infrastructure" {
  source = "./infrastructure"

  resource_group_name = "thilde"
  resource_group_location = "West Eu"
}
