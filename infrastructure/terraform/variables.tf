variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "SentinelDemo-RG"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "centralus"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "Demo"
}

variable "log_analytics_name" {
  description = "Name of Log Analytics workspace"
  type        = string
  default     = "studentportal-logs"
}

variable "acr_name" {
  description = "Name of Azure Container Registry (must be globally unique)"
  type        = string
  default     = "studentportalacr9874"   # FIXED (globally unique)

  validation {
    condition     = can(regex("^[a-zA-Z0-9]*$", var.acr_name))
    error_message = "ACR name must be alphanumeric only."
  }
}

variable "aks_cluster_name" {
  description = "Name of AKS cluster"
  type        = string
  default     = "studentportal-aks"
}

variable "aks_node_count" {
  description = "Number of nodes in AKS cluster"
  type        = number
  default     = 2
}

variable "aks_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_B2s"
}

variable "storage_account_name" {
  description = "Name of storage account (globally unique)"
  type        = string
  default     = "tfstateportal9874"   # FIXED (globally unique)

  validation {
    condition     = can(regex("^[a-z0-9]*$", var.storage_account_name))
    error_message = "Storage account name must be lowercase alphanumeric only."
  }
}
