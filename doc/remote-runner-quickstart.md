# Template Project for Digital.ai Release Integrations

This project serves as a template for developing a Python-based container plugin.

## Topics

* [Prerequisites and setup](doc/setup.md)
* [Quickstart](#quickstart) (in this document)
* [How to create your own project](#how-to-create-your-own-project) (in this document)
* [Tutorial](doc/tutorial.md)
* [Reference](doc/reference.md)
* [Guided tour: the Jenkins plugin](doc/jenkins-guided-tour.md)


## Quickstart

This section describes the quickest way to get a setup with Release and the Remote Runner and run your first container-based task. Refer to the other materials for more in-depth explanations.

The Remote Runner is the glue between the main Release application and the container tasks that are being run. It lives inside Kubernetes, registers itself with Digital.ai Release and then waits for work. When a task needs to be executed, it launches a pod to do so and takes care of the communication between task and Release.

The Quickstart assumes you have the following installed:

* Python 3
* Git
* Docker Desktop with Kubernetes enabled
* Kubectl
* Helm
* The [`xl` command line utility](https://docs.digital.ai/bundle/devops-release-version-v.22.3/page/release/how-to/install-the-xl-cli.html)

For detailed installation instructions, refer to the [Setup document](doc/setup.md).

You can do this quickstart on this template repository, or [create your own repository](#how-to-create-your-own-project) first.

### 1. Add container registry to Docker

We will build a container image that will serve as a task for Digital.ai Release. This image needs to be published somewhere so it can be picked up by the Release Remote Runner. For local development, the most convenient way is to run a local registry in Docker.

Start the registry:

    docker run -d -p 5050:5000 --name container-registry registry:2

### 2. Configure your `hosts` file

The Remote Runner needs to be able to find the other components in the system: the Release server and the registry we just installed. The easiest way to do so is to add it to your local machine's `hosts` file.

Add the following entries to `/etc/hosts`:

    127.0.0.1 digitalai.release.local
    127.0.0.1 container-registry

XXX Add: instructions for Linux / MacOS and Windows and mention that you need sudo privileges to edit

### 3. Run and configure Release

If you don't have a Release server running, you can conveniently start the Release application in Docker with the following command

    docker run --name xl-release -e ADMIN_PASSWORD=admin -e ACCEPT_EULA=Y -p 5516:5516 xebialabs/xl-release:23.1

We need to configure Release with a service user for the Remote Runner (see below) and give it the needed permissions.

Use the following command to create an account for the Remote Runner and add a unique password after `password=`

    xl apply -f dev-environment/digitalai-release-setup/remote-runnner-user.yaml --values password=

The Remote Runner needs a token to register itself with the Release server. In order to obtain a token, do the following

* Log in to release as the `remote-runner` user with the password you gave as a parameter to the `xl apply` command
* Go to the [Access tokens](http://digitalai.release.local:5516/#/personal-access-token) page: In the top-right corner, click on the **RR** icon and select **Access tokens**
* Enter a token name, for example `Local runner`, and click Generate. Copy the token and store it somewhere for future reference.

### 4. Set up the runner

Install the Remote Runner into your local Kubernetes environment with the `xl kube install` command and look closely at the answers below. Note that sometimes you can take the default, sometimes you need to give the value as prompted below and sometimes you need to give a custom value.

We've marked some questions with a warning sign where you need to pay extra attention.

```commandline
$ xl kube install 
? Following kubectl context will be used during execution: `docker-desktop`?
» Yes
? Select the Kubernetes setup where the Digital.ai Devops Platform will be installed, updated or cleaned:
»⚠️ PlainK8s [Plain multi-node K8s cluster]
? Do you want to use an custom Kubernetes namespace (current default is 'digitalai'):
» No
? Product server you want to perform install for:
»⚠️ dai-release-runner [Remote Runner for Digital.ai Release]
? Select type of image registry:
» default
? Enter the repository name (eg: <repositoryName> from <repositoryName>/<imageName>:<tagName>):
» xebialabs
? Enter the remote runner image name (eg: <imageName> from <repositoryName>/<imageName>:<tagName>):
» xlr-remote-runner
? Enter the image tag (eg: <tagName> from <repositoryName>/<imageName>:<tagName>):
» 0.1.32
? Enter the Remote Runner Helm Chart path (URL or local path):
»⚠️ /Users/hsiemelink/Code/xlr-remote-runner/helm/remote-runner
? Enter the Release URL that will be used by remote runner:
»⚠️ http://http://digitalai.release.local:5516/
? Enter the Release Token that will be used by remote runner:
»⚠️ rpa_... (Paste token here)
? Provide storage class for the remote runner: hostpath
	 -------------------------------- ----------------------------------------------------
	| LABEL                          | VALUE                                              |
	 -------------------------------- ----------------------------------------------------
	| CleanBefore                    | false                                              |
	| CreateNamespace                | true                                               |
	| ExternalOidcConf               | external: false                                    |
	| GenerationDateTime             | 20230308-152423                                    |
	| ImageNameRemoteRunner          | xlr-remote-runner                                  |
	| ImageRegistryType              | default                                            |
	| ImageTagRemoteRunner           | 0.1.32                                             |
	| IngressType                    | none                                               |
	| IsCustomImageRegistry          | false                                              |
	| K8sSetup                       | PlainK8s                                           |
	| OidcConfigType                 | no-oidc                                            |
	| OsType                         | darwin                                             |
	| ProcessType                    | install                                            |
	| RemoteRunnerHelmChartUrl       | /Users/hsiemelink/Code/xlr-remote-runner/helm/re.. |
	| RemoteRunnerReleaseUrl         | host.docker.internal                               |
	| RemoteRunnerStorageClass       | hostpath                                           |
	| RemoteRunnerToken              | rpa_9254744b183882ae604e14ac5644c05f3baa3b8c       |
	| RepositoryName                 | xebialabs                                          |
	| ServerType                     | dai-release-runner                                 |
	| ShortServerName                | other                                              |
	| UseCustomNamespace             | false                                              |
	 -------------------------------- ----------------------------------------------------
? Do you want to proceed to the deployment with these values? Yes
For current process files will be generated in the: digitalai/dai-remote-runner/digitalai/20230308-152423/kubernetes
Generated answers file successfully: digitalai/generated_answers_dai-release-runner_digitalai_install-20230308-152423.yaml 
Starting install processing.
Installing helm chart remote-runner from /Users/hsiemelink/Code/release-integration-template-python/doc/digitalai/dai-remote-runner/digitalai/20230308-152423/kubernetes/helm-chart
Installed helm chart remote-runner to namespace digitalai
```

Check the remote runner logs to see if it started correctly and is able to connect to Release.

In the Release UI, log in as **admin** and check the **Connections** page for Remote Runner connections.


### 5. Build & publish the plugin

Run the build script

Unix/macOS

* Builds the jar, image and pushes the image to the configured registry  
  ``` sh build.sh ```
* Builds the jar  
  ``` sh build.sh --jar ```
* Builds the image and pushes the image to the configured registry  
  ```  sh build.sh --image ```

Windows

* Builds the jar, image and pushes the image to the configured registry  
  ``` build.bat ```
* Builds the jar  
  ``` build.bat --jar ```
* Builds the image and pushes the image to the configured registry  
  ``` build.bat --image ```

### 6. Install plugin into Release

In Release UI, use the Plugin Manager interface to upload the jar from `build`.
The jar takes the name of the project, for example `release-integration-template-python-1.0.0.jar`.

Then:
* Restart Release container and wait for it to come up
* Refresh the UI by pressing Reload in the browser.

### 7. Test it!
Create a template with the task **Example: Hello** and run it!

### 8. Clean up

To remove the Remote Runner, issue the following command

    helm delete remote-runner -n digitalai


## How to create your own project

Create a **duplicate** of this project to start developing your own container-based integration. Note: Please do _not_ create a fork.

### Create a new repository

Before you duplicate the contents of this repository, you already need the new repository to push to.

Use the following naming convention:

    [company]-release-[target]-integration

For example: `acme-release-jenkins-integration`

Now initialize the Git repository with this name and note the url.

* Instructions to [create a repository on GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)

### Clone and duplicate

1. Open Terminal.
2. Create a bare clone of this repository.

```commandline
git clone --bare https://github.com/xebialabs/release-integration-template-python.git release-integration-temp
```

3. Mirror-push to the new repository.

```commandline
cd release-integration-template-python
git push --mirror [URL of your new repo]
```

4. Remove the temporary local repository you created earlier.

```commandline
cd ..
rm -rf release-integration-temp
```
