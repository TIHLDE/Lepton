/*
We host Lepton in Azure Container Apps. TLDR: This is a simple service
that autoscales containers, manages network, sertificates and logging.
This was the cheapest service on azure for our usecase when it was created.
*/

resource "azurerm_log_analytics_workspace" "lepton" {
  name                = "logspace"
  location            = azurerm_resource_group.lepton.location
  resource_group_name = azurerm_resource_group.lepton.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = local.common_tags
}

resource "azurerm_container_app_environment" "lepton" {
  name                       = "lepton-container-enviroment"
  location                   = azurerm_resource_group.lepton.location
  resource_group_name        = azurerm_resource_group.lepton.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.lepton.id

  infrastructure_subnet_id = azurerm_subnet.containers.id

  tags = local.common_tags
}

locals {
  lepton_cpu = {
    dev = 0.5
    pro = 1
  }
  lepton_mem = {
    dev = "1Gi"
    pro = "2Gi"
  }
}

resource "azurerm_container_app" "lepton-api" {
  name                         = "lepton-api"
  container_app_environment_id = azurerm_container_app_environment.lepton.id
  resource_group_name          = azurerm_resource_group.lepton.name
  revision_mode                = "Single"

  // Required to not delete the manually created custom domain since 
  // it is not possible to create a managed certificate for a custom domain 
  // with terraform (2023)
  lifecycle {
    ignore_changes = [ingress[0].custom_domain]
  }

  secret {
    name  = "reg-passwd"
    value = azurerm_container_registry.lepton.admin_password
  }

  registry {
    server               = azurerm_container_registry.lepton.login_server
    password_secret_name = "reg-passwd"
    username             = azurerm_container_registry.lepton.admin_username
  }

  template {
    min_replicas = var.lepton_api_min_replicas
    max_replicas = var.lepton_api_max_replicas

    container {
      name  = "lepton-api"
      image = "${azurerm_container_registry.lepton.login_server}/lepton:latest"

      cpu    = local.lepton_cpu[var.enviroment]
      memory = local.lepton_mem[var.enviroment]

      env {
        name  = "DATABASE_HOST"
        value = azurerm_mysql_flexible_server.lepton-database-server.fqdn
      }
      env {
        name  = "DATABASE_NAME"
        value = azurerm_mysql_flexible_database.lepton-database.name
      }
      env {
        name  = "DATABASE_PASSWORD"
        value = azurerm_mysql_flexible_server.lepton-database-server.administrator_password
      }
      env {
        name  = "DATABASE_USER"
        value = azurerm_mysql_flexible_server.lepton-database-server.administrator_login
      }
      env {
        name  = "DATABASE_PORT"
        value = 3306
      }
      env {
        name  = "AZURE_STORAGE_CONNECTION_STRING"
        value = azurerm_storage_account.lepton.primary_connection_string
      }
      env {
        name  = "DJANGO_SECRET"
        value = random_string.django_secret.result
      }

      env {
        name  = "EMAIL_HOST"
        value = "smtp.gmail.com"
      }
      env {
        name  = "EMAIL_PASSWORD"
        value = var.email_password
      }
      env {
        name  = "EMAIL_PORT"
        value = 587
      }
      env {
        name  = "EMAIL_USER"
        value = var.email_user
      }
      env {
        name  = "SENTRY_DSN"
        value = var.centry_dsn
      }
      env {
        name  = "CELERY_BROKER_URL"
        value = "amqp://guest:guest@rabbitmq:5672"
      }
      env {
        name  = "VIPPS_TOKEN_URL"
        value = var.vipps_token_url
      }
      env {
        name  = "VIPPS_SUBSCRIPTION_KEY"
        value = var.vipps_subscription_key
      }
      env {
        name  = "VIPPS_CALLBACK_PREFIX"
        value = var.vipps_callback_prefix
      }
      env {
        name  = "VIPPS_CLIENT_ID"
        value = var.vipps_client_id
      }
      env {
        name  = "VIPPS_CLIENT_SECRET"
        value = var.vipps_client_secret
      }
      env {
        name  = "VIPPS_COOKIE"
        value = ""
      }
      env {
        name  = "VIPPS_FALLBACK"
        value = var.vipps_fallback_url
      }
      env {
        name  = "VIPPS_FORCE_PAYMENT_URL"
        value = var.vipps_force_payment_url
      }
      env {
        name  = "VIPPS_MERCHANT_SERIAL_NUMBER"
        value = var.vipps_merchant_serial_number
      }
      env {
        name  = "VIPPS_ORDER_URL"
        value = var.vipps_order_url
      }
      env {
        name  = var.enviroment == "pro" ? "PROD" : "DEV"
        value = "true"
      }
    }
  }

  ingress {
    target_port                = 8000
    allow_insecure_connections = false
    external_enabled           = true

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = local.common_tags
}

resource "azurerm_container_app" "rabbitmq" {
  name                         = "rabbitmq"
  container_app_environment_id = azurerm_container_app_environment.lepton.id
  resource_group_name          = azurerm_resource_group.lepton.name
  revision_mode                = "Single"

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "rabbitmq"
      image  = "rabbitmq:3.9.13"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  ingress {
    target_port = 5672
    transport   = "tcp"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = local.common_tags
}

resource "azurerm_container_app" "celery" {
  name                         = "celery"
  container_app_environment_id = azurerm_container_app_environment.lepton.id
  resource_group_name          = azurerm_resource_group.lepton.name
  revision_mode                = "Single"


  secret {
    name  = "reg-passwd"
    value = azurerm_container_registry.lepton.admin_password
  }

  registry {
    server               = azurerm_container_registry.lepton.login_server
    password_secret_name = "reg-passwd"
    username             = azurerm_container_registry.lepton.admin_username
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name    = "celery"
      image   = "${azurerm_container_registry.lepton.login_server}/lepton:latest"
      cpu     = 0.25
      memory  = "0.5Gi"
      command = ["celery", "--app", "app", "worker", "--task-events", "--beat", "--loglevel", "info"]

      env {
        name  = "DATABASE_HOST"
        value = azurerm_mysql_flexible_server.lepton-database-server.fqdn
      }
      env {
        name  = "DATABASE_NAME"
        value = azurerm_mysql_flexible_database.lepton-database.name
      }
      env {
        name  = "DATABASE_PASSWORD"
        value = azurerm_mysql_flexible_server.lepton-database-server.administrator_password
      }
      env {
        name  = "DATABASE_USER"
        value = azurerm_mysql_flexible_server.lepton-database-server.administrator_login
      }
      env {
        name  = "DATABASE_PORT"
        value = 3306
      }
      env {
        name  = "AZURE_STORAGE_CONNECTION_STRING"
        value = azurerm_storage_account.lepton.primary_connection_string
      }
      env {
        name  = "DJANGO_SECRET"
        value = random_string.django_secret.result
      }

      env {
        name  = "EMAIL_HOST"
        value = "smtp.gmail.com"
      }
      env {
        name  = "EMAIL_PASSWORD"
        value = var.email_password
      }
      env {
        name  = "EMAIL_PORT"
        value = 587
      }
      env {
        name  = "EMAIL_USER"
        value = var.email_user
      }
      env {
        name  = "SENTRY_DSN"
        value = var.centry_dsn
      }
      env {
        name  = "CELERY_BROKER_URL"
        value = "amqp://guest:guest@rabbitmq:5672"
      }
      env {
        name  = "VIPPS_TOKEN_URL"
        value = var.vipps_token_url
      }
      env {
        name  = "VIPPS_SUBSCRIPTION_KEY"
        value = var.vipps_subscription_key
      }
      env {
        name  = "VIPPS_CALLBACK_PREFIX"
        value = var.vipps_callback_prefix
      }
      env {
        name  = "VIPPS_CLIENT_ID"
        value = var.vipps_client_id
      }
      env {
        name  = "VIPPS_CLIENT_SECRET"
        value = var.vipps_client_secret
      }
      env {
        name  = "VIPPS_COOKIE"
        value = ""
      }
      env {
        name  = "VIPPS_FALLBACK"
        value = var.vipps_fallback_url
      }
      env {
        name  = "VIPPS_FORCE_PAYMENT_URL"
        value = var.vipps_force_payment_url
      }
      env {
        name  = "VIPPS_MERCHANT_SERIAL_NUMBER"
        value = var.vipps_merchant_serial_number
      }
      env {
        name  = "VIPPS_ORDER_URL"
        value = var.vipps_order_url
      }
    }
  }

  tags = local.common_tags
}
