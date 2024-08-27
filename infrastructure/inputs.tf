variable "vipps_client_secret" {
  type      = string
  sensitive = true
}

variable "vipps_client_id" {
  type      = string
  sensitive = true
}

variable "vipps_subscription_key" {
  type      = string
  sensitive = true
}

variable "vipps_callback_prefix" {
  type = string
}

variable "vipps_fallback_url" {
  type = string
}

variable "vipps_force_payment_url" {
  type      = string
  sensitive = true
}
variable "vipps_order_url" {
  type      = string
  sensitive = true
}

variable "vipps_token_url" {
  type      = string
  sensitive = true
}

variable "centry_dsn" {
  type      = string
  sensitive = true
}

variable "email_user" {
  type = string
}

variable "email_password" {
  type      = string
  sensitive = true
}

variable "vipps_merchant_serial_number" {
  type      = string
  sensitive = true
}

variable "lepton_api_min_replicas" {
  type    = number
  default = 1
}

variable "lepton_api_max_replicas" {
  type    = number
  default = 1
}

variable "feide_client_id" {
  type      = string
  sensitive = true
}

variable "feide_client_secret" {
  type      = string
  sensitive = true
}

variable "feide_token_url" {
  type      = string
  default = "https://auth.dataporten.no/oauth/token"
}

variable "feide_user_groups_info_url" {
  type = string
  default = "https://groups-api.dataporten.no/groups/me/groups"
}

variable "feide_redirect_url" {
  type = string
}

variable "enviroment" {
  type        = string
  description = "value is either dev or pro"
  default     = "dev"
}
