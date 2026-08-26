variable "subscription_id" {
  description = "Azure Subscription ID som Terraform skal bruke"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "Azure Tenant ID (valgfritt, men anbefalt)"
  type        = string
  sensitive   = true
}

variable "name" {
  description = "Basenavn for ressurser"
  type        = string
  default     = "jumpbox"
}

variable "location" {
  type        = string
  description = "Azure region for jumpbox-RG (f.eks. Norway East)"
  default     = "northeurope"
}

variable "admin_username" {
  description = "Adminbruker på jumpbox."
  type        = string
}

variable "ssh_public_keys" {
  description = "Liste med én eller flere SSH public keys (innhold av .pub-filer)."
  type        = list(string)
  default     = []
}

variable "jumpbox_vm_size" {
  description = "VM-størrelse."
  type        = string
  default     = "Standard_B1s"
}

variable "prod_rg_name" {
  description = "Navn på eksisterende prod-RG med VNet og DB"
  type        = string
  default     = "tihlde-pro"
}

variable "prod_vnet_name" {
  description = "Navn på eksisterende prod-VNet"
  type        = string
  default     = "lepton-network"
}

variable "prod_mysql_name" {
  description = "Navn på eksisterende MySQL Flexible Server i prod"
  type        = string
  default     = "lepton-database-pro"
}
