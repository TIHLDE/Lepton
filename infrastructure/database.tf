/*
Everything related to the cloud databse setup is defined here.
It is important that we NEVER do changes to database resouces
that will affect the user data. If you se "destroy" in the
terraform plan on vital database resources... ask your elders if 
it is ok.
*/

resource "azurerm_mysql_flexible_server" "lepton-database-server" {
  name                   = "lepton-database-${terraform.workspace}"
  resource_group_name    = azurerm_resource_group.lepton.name
  location               = azurerm_resource_group.lepton.location
  administrator_login    = random_string.database_username.result
  administrator_password = random_password.database_password.result
  delegated_subnet_id    = azurerm_subnet.database.id
  private_dns_zone_id    = azurerm_private_dns_zone.lepton.id

  // We can only roll back the database 7 days
  backup_retention_days        = 7
  sku_name                     = local.database_sku[terraform.workspace]
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

// This setting was off when we moved to terraform 
// and after testing it, it is required or else our migrations won't apply correctly
resource "azurerm_mysql_flexible_server_configuration" "sql_generate_invisible_primary_key" {
  name                = "sql_generate_invisible_primary_key"
  resource_group_name = azurerm_resource_group.lepton.name
  server_name         = azurerm_mysql_flexible_server.lepton-database-server.name
  value               = "OFF"
}

// The database and backend are in a closed network inside Azure so
// it is not that important to keep encrypt network trafic
resource "azurerm_mysql_flexible_server_configuration" "require_secure_transport" {
  name                = "require_secure_transport"
  resource_group_name = azurerm_resource_group.lepton.name
  server_name         = azurerm_mysql_flexible_server.lepton-database-server.name
  value               = "OFF"
}

// We store everything inside one mysql databse
// NEVER delete this resource in prod!
resource "azurerm_mysql_flexible_database" "lepton-database" {
  name                = "db"
  resource_group_name = azurerm_resource_group.lepton.name
  server_name         = azurerm_mysql_flexible_server.lepton-database-server.name
  charset             = "utf8mb4"
  collation           = local.database_collation[var.enviroment]
}

locals {
  // sku is the different machines that we rent from Azure.
  // We use a cheaper one for dev, and a more expensive for pro.
  // There might be wiggleroom in what machine size we need.
  database_sku = {
    dev = "B_Standard_B1s"
    pro = "B_Standard_B2s"
  }
  // WHY DO WE HAVE DIFFERENT collation?
  // this is left over from a bug that happend back in 2023...
  // long story short. "utf8mb4_unicode_ci" is the correct format.
  // Getting dev and pro back in sync is done by nuking dev enviroment
  // and build it up with the same collation as pro enviroment.
  // do not change this in prod, as it will result in data loss.
  database_collation = {
    dev = "utf8mb4_0900_ai_ci"
    pro = "utf8mb4_unicode_ci"
  }
}
