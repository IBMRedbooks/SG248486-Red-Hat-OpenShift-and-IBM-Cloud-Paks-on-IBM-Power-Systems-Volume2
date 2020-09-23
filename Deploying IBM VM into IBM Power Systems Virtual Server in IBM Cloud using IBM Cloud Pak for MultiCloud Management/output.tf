#Displays the IP address assigned
output "vm-ip" {
  value = ibm_pi_instance.PowerVS_instance.addresses
}