resource "azurerm_service_plan" "lepton" {
  name                = "lepton-${random_integer.lepton.result}"
  resource_group_name = azurerm_resource_group.lepton.name
  location            = azurerm_resource_group.lepton.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "lepton" {
  name                = "lepton-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.lepton.name
  location            = azurerm_service_plan.lepton.location
  service_plan_id     = azurerm_service_plan.lepton.id
  https_only          = true

  virtual_network_subnet_id     = azurerm_subnet.lepton_web.id
  public_network_access_enabled = true
  
  // TODO: add more settings that we use
  app_settings = {
    DATABASE_HOSTNAME = azurerm_private_dns_zone.lepton.name
    DATABASE_NAME     = azurerm_mysql_flexible_database.lepton.name
    DATABASE_USERNAME = var.database_username
    DATABASE_PASSWORD = var.database_password
  }

  site_config {
    minimum_tls_version = "1.2"

    application_stack {
      docker_image_name        = var.docker_image
      docker_registry_url      = azurerm_container_registry.lepton.login_server
      docker_registry_username = azurerm_container_registry.lepton.admin_username
      docker_registry_password = azurerm_container_registry.lepton.admin_password
      python_version           = "3.7"
    }
  }
}
