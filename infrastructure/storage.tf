// This is where the images/pdf/uploads is stored for lepton
resource "azurerm_storage_account" "lepton" {
  name                     = "leptonstorage${var.enviroment}"
  resource_group_name      = azurerm_resource_group.lepton.name
  location                 = azurerm_resource_group.lepton.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  min_tls_version          = "TLS1_2"

  tags = local.common_tags

  lifecycle {
    prevent_destroy = true
  }
}
