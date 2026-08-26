#########################
# Jumpbox & nettverk
#########################

output "jumpbox_resource_group" {
  description = "Ressursgruppen der jumpbox-ressursene ligger."
  value       = azurerm_resource_group.rg.name
}

output "jumpbox_public_ip" {
  description = "Offentlig IP til jumpbox."
  value       = azurerm_public_ip.pip.ip_address
}

output "jumpbox_private_ip" {
  description = "Privat IP til jumpbox (i prod-VNet)."
  value       = azurerm_network_interface.nic.private_ip_address
}

output "jumpbox_vm_id" {
  description = "Resource ID til VM'en."
  value       = azurerm_linux_virtual_machine.vm.id
}

output "jumpbox_nic_id" {
  description = "Resource ID til NIC."
  value       = azurerm_network_interface.nic.id
}

#########################
# DB-info (fra prod)
#########################

output "db_fqdn" {
  description = "FQDN til MySQL Flexible Server i prod."
  value       = local.db_fqdn
}

#########################
# Klare kommandoer
#########################

output "ssh_command" {
  description = "SSH rett inn på jumpbox."
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.pip.ip_address}"
}

output "ssh_tunnel_command" {
  description = "Tunnel lokal 3306 -> prod-DB via jumpbox."
  value       = "ssh -N -L 3306:${local.db_fqdn}:${local.db_port} ${var.admin_username}@${azurerm_public_ip.pip.ip_address}"
}
