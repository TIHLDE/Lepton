resource "azurerm_resource_group" "lepton" {
  name     = "tihlde-${var.enviroment}"
  location = "northeurope"

  tags = local.common_tags
}

resource "random_password" "database_password" {
  length           = 18
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "random_string" "database_username" {
  length  = 16
  special = false
}

resource "random_string" "django_secret" {
  length  = 32
  special = true
}

output "acr_admin_username" {
  value = azurerm_container_registry.lepton.admin_username
}

output "acr_admin_password" {
  value = azurerm_container_registry.lepton.admin_password
}

output "acr_login_server" {
  value = azurerm_container_registry.lepton.login_server
}

locals {
  common_tags = {
    environment = "${var.enviroment}"
    workspace   = "${terraform.workspace}"
    team        = "index"
    managed_by  = "terraform"
  }
}
