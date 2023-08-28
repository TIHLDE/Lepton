resource "azurerm_private_dns_zone" "lepton" {
  name                = local.database_internal_hostname
  resource_group_name = azurerm_resource_group.lepton.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "lepton" {
  name                  = "exampleVnetZone.com"
  private_dns_zone_name = azurerm_private_dns_zone.lepton.name
  virtual_network_id    = azurerm_virtual_network.lepton.id
  resource_group_name   = azurerm_resource_group.lepton.name
}

resource "azurerm_mysql_flexible_server" "lepton" {
  name                         = "example-mysql"
  resource_group_name          = azurerm_resource_group.lepton.name
  location                     = azurerm_resource_group.lepton.location
  administrator_login          = var.database_username
  administrator_password       = var.database_password
  backup_retention_days        = 7
  delegated_subnet_id          = azurerm_subnet.lepton_db.id
  private_dns_zone_id          = azurerm_private_dns_zone.lepton.id
  sku_name                     = "GP_Standard_D2ds_v4"
  geo_redundant_backup_enabled = false
  version                      = "8.0.21"
  zone                         = "1"

  maintenance_window {
    day_of_week  = 0
    start_hour   = 8
    start_minute = 0
  }

  storage {
    iops    = 360
    size_gb = 20
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.lepton]
}

resource "azurerm_mysql_flexible_database" "lepton" {
  charset             = "utf8mb4"
  collation           = "utf8mb4_unicode_ci"
  name                = "mysqlfsdb_${random_string.name.result}"
  resource_group_name = azurerm_resource_group.lepton.name
  server_name         = azurerm_mysql_flexible_server.lepton.name
}
