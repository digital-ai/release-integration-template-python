## Prerequisites for container-based plugin development

In order to use the Digital.ai Release Integration SDK for Python, you will need:

* Python 3 
* Git
* Docker

## Prerequisites for running container-based plugins in production

To run container-based tasks in a production environment, you need:

* Digital.ai Release 
* A Kubernetes cluster. We support the following environments:
  * AWS EKS
  * Azure AKS
  * Google Cloud Platform
  * OpenShift

To install the Remote Runner agent that will run the container-based tasks into kubernetes, you will need:

* Digital.ai `xl` command line utility
* kubectl
* helm


XXX Add links and a bit more text. We don't need to do a step-by-step of every third-party tool.