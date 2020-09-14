provider "openstack" {
  insecure = true
  }
#Create an IBM i partition
resource "openstack_compute_instance_v2" "PowerVC-LPAR" {
  name         = "${var.ibm_stack_name}"  
  image_name   = "${var.openstack_image_name}"
  flavor_name  = "${var.openstack_flavor_name}"   
  
  network {
    name = "${var.openstack_network_name}"
   }
 }
 #Variables for deployment
variable "openstack_image_name" {
  description = "The Name of the image to be used for deployment."
}

variable "openstack_flavor_name" {
  description = "The Name of the flavor to be used for deployment."
}

variable "openstack_network_name" {
  description = "The Name of the network to be used for deployment."
}

variable "ibm_stack_name" {
  description = "Name of the new LPAR to deploy"
}

output "New IP for LPAR" {
  value = "${openstack_compute_instance_v2.PowerVC-LPAR.*.network.0.fixed_ip_v4}"
 }
