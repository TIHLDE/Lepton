resource "azurerm_container_registry" "lepton" {
  name                = var.registry_name
  resource_group_name = azurerm_resource_group.lepton.name
  location            = azurerm_resource_group.lepton.location
  sku                 = "Premium"
  admin_enabled       = false
}
