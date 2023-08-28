resource "azurerm_resource_group" "lepton" {
  name     = "${var.resource_group_name}-${random_integer.lepton.result}"
  location = var.resource_group_location

  tags = {
    environment = terraform.workspace
  }
}

resource "random_integer" "lepton" {
  min = 10000
  max = 99999
}

resource "random_string" "name" {
  length  = 8
  lower   = true
  numeric = false
  special = false
  upper   = false
}

locals {
  database_internal_hostname = "leptondb.mysql.database.azure.com"
}
