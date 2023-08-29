resource "azurerm_mysql_flexible_server" "lepton-database-server" {
  name                         = "lepton-database-${terraform.workspace}"
  resource_group_name          = azurerm_resource_group.lepton.name
  location                     = azurerm_resource_group.lepton.location
  administrator_login          = random_string.database_username.result
  administrator_password       = random_password.database_password.result
  delegated_subnet_id          = azurerm_subnet.database.id
  private_dns_zone_id          = azurerm_private_dns_zone.lepton.id
  backup_retention_days        = 7
  sku_name                     = "B_Standard_B1s"
  geo_redundant_backup_enabled = false
  version                      = "8.0.21"
  zone                         = "1"

  storage {
    iops    = 360
    size_gb = 20
  }

  tags = local.common_tags

  depends_on = [azurerm_private_dns_zone_virtual_network_link.lepton]
}

resource "azurerm_mysql_flexible_server_configuration" "sql_generate_invisible_primary_key" {
  name                = "sql_generate_invisible_primary_key"
  resource_group_name = azurerm_resource_group.lepton.name
  server_name         = azurerm_mysql_flexible_server.lepton-database-server.name
  value               = "OFF"
}

resource "azurerm_mysql_flexible_server_configuration" "require_secure_transport" {
  name                = "require_secure_transport"
  resource_group_name = azurerm_resource_group.lepton.name
  server_name         = azurerm_mysql_flexible_server.lepton-database-server.name
  value               = "OFF"
}

resource "azurerm_mysql_flexible_database" "lepton-database" {
  name                = "db"
  resource_group_name = azurerm_resource_group.lepton.name
  server_name         = azurerm_mysql_flexible_server.lepton-database-server.name
  charset             = "utf8mb4"
  collation           = "utf8mb4_0900_ai_ci"
}
