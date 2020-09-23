## Heat template to deploy openshift cluster in openstack

This heat template will deploy an openshift cluster of 3 master nodes and 3 to 6 workers.

### Prereqs

Access to an existing Openstack project
A Redhat subscription pull secret which is required for deploy openshift
The network id of the Openstack project network on which to allocate new subnets
The public key of an openstack keypair that will be used to access the instances.

### Usage

The Heat template consists of two files and environemnt file and a deployment template

ocpenvironment.file - This defines the input variables to deployment template
openshiftdeploy-ppc64le.yaml - This defines the execution of the deployment for use on ppcle architecture
openshiftdeploy-x86_64.yaml - This defines the execution of the deployment for use on x86_64 architecture
The variables in the ocpenvironment.file are

num_workers: - defaults to 3
cluster_name: - The name to call the ocp cluster
openshift_version: defaults to 4.3.24. Or a valid directory version in https://mirror.openshift.com/pub/openshift-v4/clients/ocp/
worker_flavor: - A valid Openstack flavor name defaults to m1.large
master_flavor: - A valid Openstack flavor name defaults to m1.large
internal_network_cidr: - the cidr definition for the internal project subnet that will be created eg 10.20.0.0/24. This will be used by the cluster instances.
infrastructure_node_ip: - the ip address used for the Bastion node this must be in the subnet above. eg 10.20.0.10
internal_network_id: - This is the UUID of the internal project network that is used. It must be the ID not the name. This is where the subnet will be created that uses the internal_network_cidr.
pullSecret: - A Redhat subscription pull secret which is required for deploy openshift
key_name: - The Openstack key-pair name to be used to deploy the bastion.
public_key: - The public key of an openstack keypair used to deploy the Bastion this will be injected into ocp nodes via the iginition file so that SSH can be used to access nodes. This can be obtained by viewing the Key Pair in the Horizon UI. Project -> Compute -> Key
Creating the Cluster

To deploy the cluster you can use the Horizon menu

Project -> Orchestration -> Stacks -> Launch Stack

This will display a popup and you will be prompted for

A template file - Use the openshiftdeploy.yaml
An environment file - Use the ocpenvironment.file
Pressing NEXT will then give you a list of the variables used and also prompt for any other required information.

The status of the stack can be viewed from the Project -> Orchestration -> Stacks.

NOTE Cluster deployment can take between 30-mins to 60 mins dependent on the cluster size. Even if the stack status shows Create Complete this does not mean the OCP cluster deployment is complete it indicates all the resources have been instantiated to enable the OCP depolyment

To validate whether the deployment is complete

login to the bastion infrastructure node using the cloudusr userid ssh cloudusr@<bastion ip> -i <your private key>
sudo to root sudo su -
Change directory to /var/www/html/ignition/ eg cd /var/www/html/ignition/baztest43
Enter openshift-install wait-for install-complete this will give you information if the install is complete or will wait until the install finished. If the install is complete you will see something like the following.
INFO Waiting up to 30m0s for the cluster at https://api.baz43test.hur.hdclab.intranet.ibm.com:6443 to initialize... 
INFO Waiting up to 10m0s for the openshift-console route to be created... 
INFO Install complete!                            
INFO To access the cluster as the system:admin user when using 'oc', run 'export KUBECONFIG=/var/www/html/ignition/baz43test/auth/kubeconfig' 
INFO Access the OpenShift web-console here: https://console-openshift-console.apps.baz43test.hur.hdclab.intranet.ibm.com 
INFO Login to the console with user: kubeadmin, password: <cluster password>
Post Deployment

The bastion node floating ip address needs to be added to the list of DNS servers on any clients that need to access the cluster
Openshift operator commands can be issued to the cluster from the Bastion infrastructure node.
login to the bastion infrastructure node using the cloudusr userid ssh cloudusr@<bastion ip> -i <your private key>
sudo to root sudo su -
Issue the command to setup the KUBECONFIG environment variable as stated in the response from openshift-install wait-for install-complete
You can now issue oc commands to the openshift cluster. eg oc status or oc get nodes
If you require persistent volumes an NFS server has been installed on the Bastion and the entire /export directory has been shared out. To setup NFS volumes for ocp login to the Bastion sudo to root and issue helpernodecheck nfs-info which gives instructions on how this can be performed.
To access the openshift nodes directly you can add a floating ip to the master/worker node and login directly from your client using your openstack ssh key but you should logn using userid core. Alternatively you can add your private key on the Bastion node.
Removing/Destroying the Cluster

To delete the cluster use the Delete Stacks from Project -> Orchestration -> Stacks , do not delete the instances individually as this will not cleanup all the deployed resources.

Overview of heat template

Creates a new openstack subnet on the project network that was identified in the template for ocp cluster deployment
Creates a virtual router for the network
Create neutron network ports for all the instances of the cluster
Creates a security group with default firewall rules
Allocates floating ips to the neutron ports
Creates a CentOS 7 bastion node which will contain the DNS and used to deploy the Openshift cluster. This uses https://github.com/RedHatOfficial/ocp4-helpernode.git to configure and deploy the Bastion node.
Downloads the openshift code and updates the openshift cluster configuration
Deploys Redhat CoreOS bootstrap and master nodes. This involves chain linking a basic RHCOS ignition file to the openshift ignition files on the bastion.
After the bootstrap and masters are deployed deploys 3-6 worker nodes using the same approach as the master and bootstrap nodes.
