resource "azurerm_container_registry" "lepton" {
  name                = "leptonregistry${var.enviroment}"
  resource_group_name = azurerm_resource_group.lepton.name
  location            = azurerm_resource_group.lepton.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = local.common_tags
}
