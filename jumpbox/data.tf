# Slå opp eksisterende prod-RG (hardkodet navn)
data "azurerm_resource_group" "prod" {
  name = var.prod_rg_name
}

# Slå opp eksisterende VNet
data "azurerm_virtual_network" "prod_vnet" {
  name                = var.prod_vnet_name
  resource_group_name = data.azurerm_resource_group.prod.name
}

# Slå opp MySQL Flexible Server i prod
data "azurerm_mysql_flexible_server" "prod_mysql" {
  name                = var.prod_mysql_name
  resource_group_name = data.azurerm_resource_group.prod.name
}

# Praktisk info til outputs/bruk
locals {
  prod_vnet_id = data.azurerm_virtual_network.prod_vnet.id
  db_fqdn      = data.azurerm_mysql_flexible_server.prod_mysql.fqdn
  db_port      = 3306
}
