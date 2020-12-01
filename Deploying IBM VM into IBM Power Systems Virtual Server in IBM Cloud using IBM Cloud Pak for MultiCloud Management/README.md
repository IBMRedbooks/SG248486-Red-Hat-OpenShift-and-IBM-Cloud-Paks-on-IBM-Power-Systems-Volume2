# Deploying IBM VM into IBM Power Systems Virtual Server in IBM Cloud using IBM Cloud Pak for Multicloud Management
IBM Power Systems clients who have typically relied upon on-premise private cloud solution
includes IBM PowerVC that provides the infrastructure-as-a-service (IaaS) layer. Now can quickly and economically extend their IT resources onto IBM Power Systems Virtual Servers.

IBM Power Systems Virtual Servers on IBM Cloud integrates AIX and IBM i capabilities into the IBM Cloud experience. Users receive fast, self-service provisioning, flexible management and access to a stack of enterprise IBM Cloud services - all with easy Pay-As-you-use billing

Using IBM Cloud Pak for Multicloud Management that provides advanced multicloud management capabilities through Cloud Automation Manager that enables connectivity to IBM Power Systems Virtual Server in IBM Cloud to streamline virtual machine deployments.

From that perspective, we describe how to deploy IBM i virtual machine by using IBM Cloud Pak for MultiCloud Management into IBM Power Virtual Servers in IBM Cloud.

Before you create your first Power Virtual Server instance, review the following prerequisites: 
- Create an IBM Cloud account.
- Review the Identify and Access Management (IAM) information.
- Create a public and private ssh key that you can use to securely connect to your IBM Power Virtual Server.
- If you want to use a custom AIX or IBM i image, you must create an IBM Cloud Object Storage (COS) and upload it there.
- If you want to use private network to connect to an IBM Power Virtual Server instance, you must order the Direct Link Connect service. You cannot create a private network during the VM provisioning process. You must first use the Power Virtual Server user interface, command line interface (CLI), or application programming interfaced (API) to create one (optional).
