provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

provider "databricks" {
  host = var.databricks_host
}

resource "azurerm_resource_group" "governance" {
  name     = "rg-${var.project_name}-governance-${var.environment}"
  location = var.location
}

# --- Governance Control Plane (AKS) ---

resource "azurerm_kubernetes_cluster" "governance_k8s" {
  name                = "aks-unity-iq-${var.environment}"
  location            = azurerm_resource_group.governance.location
  resource_group_name = azurerm_resource_group.governance.name
  dns_prefix          = "governance-k8s"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }
}

# --- Governance Metadata Store (Postgres) ---

resource "azurerm_postgresql_flexible_server" "metadata" {
  name                   = "psql-governance-metadata-${var.environment}"
  resource_group_name    = azurerm_resource_group.governance.name
  location               = azurerm_resource_group.governance.location
  version                = "13"
  administrator_login    = "govadmin"
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "GP_Standard_D2ds_v4"
}

# --- Unity Catalog Metastore Foundation (Azure Example) ---

resource "azurerm_storage_account" "metastore_root" {
  name                     = "stmetastroot${var.environment}"
  resource_group_name      = azurerm_resource_group.governance.name
  location                 = azurerm_resource_group.governance.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # Required for ADLS Gen2
}

resource "azurerm_storage_data_lake_gen2_filesystem" "metastore" {
  name               = "metastore-root"
  storage_account_id = azurerm_storage_account.metastore_root.id
}

# --- Multi-Cloud Governance (AWS S3 External Location) ---

resource "aws_s3_bucket" "external_data" {
  bucket = "db-governed-data-vault-${var.environment}"
}
