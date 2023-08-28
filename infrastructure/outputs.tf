output "azurerm_mysql_flexible_server" {
  value = azurerm_mysql_flexible_server.lepton.name
}

output "admin_login" {
  value = azurerm_mysql_flexible_server.lepton.administrator_login
}
