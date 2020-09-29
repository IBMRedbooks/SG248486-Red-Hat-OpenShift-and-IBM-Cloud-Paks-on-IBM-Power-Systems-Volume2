provider "ibm" {
  version = "~> 1.12"
  ibmcloud_api_key = var.ibmcloud_api_key
  region           = var.ibmcloud_region
}
