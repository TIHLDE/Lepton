resource "azurerm_virtual_network" "lepton" {
  name                = "tihldenetwork"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.lepton.location
  resource_group_name = azurerm_resource_group.lepton.name
}

resource "azurerm_subnet" "lepton_db" {
  name                 = "lepton-database-subnet"
  resource_group_name  = azurerm_resource_group.lepton.name
  virtual_network_name = azurerm_virtual_network.lepton.name
  address_prefixes     = ["10.0.1.0/24"]
  service_endpoints    = ["Microsoft.Storage"]
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

resource "azurerm_subnet" "lepton_web" {
  name                 = "lepton-web-subnet"
  resource_group_name  = azurerm_resource_group.lepton.name
  virtual_network_name = azurerm_virtual_network.lepton.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.Web"]
  delegation {
    name = "web"

    service_delegation {
      name = "Microsoft.Web/serverFarms"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}