terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">3.68.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "devops"
    storage_account_name = "tfstatetihlde"
    container_name       = "tfstate"
    key                  = "lepton.tfstate"
  }
}

provider "azurerm" {
  features {}

  skip_provider_registration = true
}

module "infrastructure" {
  source = "./infrastructure"

  email_password = var.email_password
  email_user     = var.email_user

  centry_dsn = var.centry_dsn

  enviroment = var.enviroment

  vipps_callback_prefix        = var.vipps_callback_prefix
  vipps_subscription_key       = var.vipps_subscription_key
  vipps_client_id              = var.vipps_client_id
  vipps_client_secret          = var.vipps_client_secret
  vipps_merchant_serial_number = var.vipps_merchant_serial_number
  vipps_fallback_url           = var.vipps_fallback_url
  vipps_token_url              = var.vipps_token_url
  vipps_force_payment_url      = var.vipps_force_payment_url
  vipps_order_url              = var.vipps_order_url

  lepton_api_min_replicas = var.lepton_api_min_replicas
  lepton_api_max_replicas = var.lepton_api_max_replicas

  feide_client_id            = var.feide_client_id
  feide_client_secret        = var.feide_client_secret
  feide_token_url            = var.feide_token_url
  feide_user_groups_info_url = var.feide_user_groups_info_url
  feide_redirect_url         = var.feide_redirect_url
}
