provider "openstack" {
  insecure = true
}

#Create an IBM i partition
resource "openstack_compute_instance_v2" "PowerVC-VM" {
  name        = var.ibm_stack_name
  image_name  = var.openstack_image_name
  flavor_name = var.openstack_flavor_name

  network {
    name = var.openstack_network_name
  	}
}

#Variables for deployment
variable "openstack_image_name" {
  description = "Please insert the name of the image of PowerVC."
}

variable "openstack_flavor_name" {
  description = "Please insert the Compute Template or flavor to deploy the virtual machine."
}

variable "openstack_network_name" {
  description = "Please insert the name of the network."
}

variable "ibm_stack_name" {
  description = "Please insert a new name for the Virtual Machine"
}

output "VM_IP_Address" {
  value = openstack_compute_instance_v2.PowerVC-VM.*.network.0.fixed_ip_v4
}
