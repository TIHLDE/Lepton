variable "resource_group_location" {
  type        = string
  description = "The Azure Region in which all resources in this example should be created."
  default     = "West Europe"
}

variable "resource_group_name" {
  type        = string
  description = "The name of the resource group in which all resources in this example should be created."
}

variable "registry_name" {
  default = "Name of the container registry"
}

variable "docker_image" {
  default = "Docker image to deploy"
}

variable "database_username" {
  default = "Username for the database"
}

variable "database_password" {
  default = "Password for the database"
}
