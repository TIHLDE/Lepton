resource "azurerm_network_security_group" "lepton" {
  name                = "database-security-group"
  location            = azurerm_resource_group.lepton.location
  resource_group_name = azurerm_resource_group.lepton.name

  tags = local.common_tags
}

resource "azurerm_virtual_network" "lepton" {
  name                = "lepton-network"
  location            = azurerm_resource_group.lepton.location
  resource_group_name = azurerm_resource_group.lepton.name
  address_space       = ["10.0.0.0/16"]

  tags = local.common_tags
}

resource "azurerm_subnet" "database" {
  name                 = "database-subnet"
  resource_group_name  = azurerm_resource_group.lepton.name
  virtual_network_name = azurerm_virtual_network.lepton.name

  // We don't need this large network space for our databse
  // but it made segmentation easier.
  address_prefixes = ["10.0.8.0/21"]

  delegation {
    name = "fs"
    service_delegation {
      name = "Microsoft.DBforMySQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_subnet" "containers" {
  name                 = "containers-subnet"
  resource_group_name  = azurerm_resource_group.lepton.name
  virtual_network_name = azurerm_virtual_network.lepton.name

  address_prefixes = ["10.0.16.0/21"]
}

resource "azurerm_private_dns_zone" "lepton" {
  name                = "leptondatabase.mysql.database.azure.com"
  resource_group_name = azurerm_resource_group.lepton.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "lepton" {
  name                  = "internal.tihlde.no"
  private_dns_zone_name = azurerm_private_dns_zone.lepton.name
  virtual_network_id    = azurerm_virtual_network.lepton.id
  resource_group_name   = azurerm_resource_group.lepton.name
}
